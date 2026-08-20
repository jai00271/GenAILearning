#!/usr/bin/env python3
"""Serve GenAI Gurukul from repo root and proxy Ask-Gurukul chat to Cursor SDK."""

from __future__ import annotations

import atexit
import json
import os
import queue
import socket
import sys
import threading
import time
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("GURUKUL_PORT", "8080"))
MODEL = os.environ.get("GURUKUL_TUTOR_MODEL", "auto")


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv(ROOT / ".env")


def api_key() -> str:
    return (os.environ.get("CURSOR_API_KEY") or "").strip()


def json_bytes(payload: dict, status: int = 200):
    body = json.dumps(payload).encode("utf-8")
    return status, "application/json; charset=utf-8", body


def _patch_bridge_discovery_for_windows() -> None:
    """cursor-sdk uses select() on stderr pipes; that raises WinError 10038."""
    if os.name != "nt":
        return
    import cursor_sdk._bridge as bridge_mod
    from cursor_sdk.errors import CursorSDKError

    def _read_discovery_windows(process, timeout: float):
        if process.stderr is None:
            raise CursorSDKError("Bridge process stderr is unavailable")

        lines: queue.Queue[str | BaseException | None] = queue.Queue()

        def _reader() -> None:
            try:
                for line in process.stderr:
                    lines.put(line)
            except BaseException as exc:
                lines.put(exc)
            finally:
                lines.put(None)

        threading.Thread(target=_reader, daemon=True).start()
        deadline = time.monotonic() + timeout
        stderr_lines: list[str] = []
        pending_exc: BaseException | None = None

        while time.monotonic() < deadline:
            try:
                item = lines.get(timeout=0.1)
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if item is None:
                break
            if isinstance(item, BaseException):
                pending_exc = item
                break
            stderr_lines.append(item)
            discovery = bridge_mod.parse_discovery_line(item)
            if discovery is not None:
                return discovery

        if pending_exc is not None:
            raise CursorSDKError(f"Bridge discovery failed: {pending_exc}") from pending_exc
        exit_code = process.poll()
        if exit_code is not None:
            raise CursorSDKError(
                f"Bridge exited before discovery with status {exit_code}: "
                + "".join(stderr_lines)
            )
        raise CursorSDKError("Timed out waiting for bridge discovery")

    bridge_mod._read_discovery = _read_discovery_windows


_CLIENT = None
_AGENTS: dict[str, object] = {}
_AGENT_LOCK = threading.Lock()


def get_cursor_client():
    global _CLIENT
    if _CLIENT is None:
        from cursor_sdk import CursorClient

        _CLIENT = CursorClient.launch_bridge(workspace=str(ROOT))
        atexit.register(lambda: _CLIENT.close() if _CLIENT else None)
    return _CLIENT


def page_prompt(question: str, context: dict, first_turn: bool) -> str:
    module_id = (context or {}).get("moduleId") or "unknown"
    title = (context or {}).get("title") or ""
    url = (context or {}).get("url") or ""
    excerpt = ((context or {}).get("excerpt") or "").strip()
    if len(excerpt) > 8000:
        excerpt = excerpt[:8000] + "\n…[truncated]"

    if not first_turn:
        return (
            f"Learner is still on {module_id} — {title}\n"
            f"Page: {url}\n\n"
            f"Question:\n{question.strip()}"
        )

    return f"""You are GenAI Gurukul's in-lesson tutor.

The learner is reading: {module_id} — {title}
Page URL: {url}

Rules:
- Answer in Hinglish unless they ask for English.
- Be precise and engineer-first. Use short ASCII/mermaid diagrams when they help.
- Do NOT edit, create, or delete any files in this repo.
- Do NOT dump full lab solutions unless they explicitly ask for the solution.
- Use the lesson excerpt and repo only as reference.

Lesson excerpt:
{excerpt or "(no excerpt)"}

Question:
{question.strip()}
"""


def run_cursor(question: str, context: dict, agent_id: str | None):
    from cursor_sdk import AgentOptions, CursorAgentError, LocalAgentOptions

    key = api_key()
    if not key:
        raise RuntimeError(
            "CURSOR_API_KEY missing. Put it in .env at the repo root "
            r"(C:\Users\JAI\Documents\LEARN\GEN AI\.env)."
        )

    # Ask-only: empty toolset (no shell/edit). Safer than a long disallowed_tools list.
    opts = AgentOptions(
        model=MODEL,
        api_key=key,
        local=LocalAgentOptions(cwd=str(ROOT)),
        tools=[],
    )
    first_turn = not agent_id
    prompt = page_prompt(question, context, first_turn=first_turn)
    client = get_cursor_client()

    with _AGENT_LOCK:
        try:
            agent = None
            if agent_id and agent_id in _AGENTS:
                agent = _AGENTS[agent_id]
            elif agent_id:
                try:
                    agent = client.agents.resume(agent_id, opts)
                except Exception:
                    agent = None
            if agent is None:
                agent = client.agents.create(opts)
            _AGENTS[getattr(agent, "agent_id", "") or ""] = agent

            run = agent.send(prompt)
            result = run.wait()
            text = (run.text() or "").strip() or (getattr(result, "result", None) or "").strip()
            status = getattr(result, "status", None) or "finished"
            status_s = str(status)
            ok = status_s == "finished" or status is None
            payload: dict = {
                "ok": ok,
                "text": text,
                "agentId": getattr(agent, "agent_id", None) or agent_id,
                "status": status_s,
                "runId": getattr(result, "id", None) or getattr(run, "id", None),
            }
            if not ok:
                payload["error"] = (
                    text
                    or f"Cursor run failed (status={status_s}, model={MODEL}). "
                    "serve.py restart karo; GURUKUL_TUTOR_MODEL=auto try karo; "
                    "Cursor account pe agent/API access check karo."
                )
            return payload
        except CursorAgentError as err:
            raise RuntimeError(f"Cursor agent failed to start: {err}") from err


class GurukulServer(ThreadingHTTPServer):
    # Windows SO_REUSEADDR lets two processes share :8080 → ERR_EMPTY_RESPONSE.
    allow_reuse_address = False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        try:
            if self.path.split("?", 1)[0] == "/api/tutor/health":
                status, ctype, body = json_bytes(
                    {
                        "ok": True,
                        "hasKey": bool(api_key()),
                        "model": MODEL,
                        "bridgeReady": _CLIENT is not None,
                    }
                )
                self._send(status, ctype, body)
                return
            super().do_GET()
        except Exception:
            traceback.print_exc()
            try:
                self.send_error(500, "Internal error")
            except Exception:
                pass

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/api/tutor":
            self.send_error(404, "Not found")
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            status, ctype, body = json_bytes({"ok": False, "error": "Invalid JSON"}, 400)
            self._send(status, ctype, body)
            return

        question = str(payload.get("question") or "").strip()
        if not question:
            status, ctype, body = json_bytes({"ok": False, "error": "Question required"}, 400)
            self._send(status, ctype, body)
            return

        context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
        agent_id = str(payload.get("agentId") or "").strip() or None
        try:
            result = run_cursor(question, context, agent_id)
            status, ctype, body = json_bytes(result)
            self._send(status, ctype, body)
        except Exception as err:
            traceback.print_exc()
            status, ctype, body = json_bytes(
                {"ok": False, "error": str(err) or "Tutor failed"},
                503,
            )
            self._send(status, ctype, body)


def main() -> None:
    try:
        import cursor_sdk  # noqa: F401
    except ImportError:
        print("Missing cursor-sdk. Run:  pip install cursor-sdk", file=sys.stderr)
        sys.exit(1)

    if not api_key():
        print(
            "WARNING: CURSOR_API_KEY not set. Add it to .env then restart serve.py.",
            file=sys.stderr,
        )

    _patch_bridge_discovery_for_windows()
    print("Starting Cursor tutor bridge (first launch can take ~20s)...", flush=True)
    try:
        get_cursor_client()
        print("Cursor bridge ready.", flush=True)
    except Exception as err:
        print(f"WARNING: Cursor bridge failed to start: {err}", file=sys.stderr, flush=True)
        traceback.print_exc()

    # IPv4 only. Windows `localhost` often hits ::1 and DualStack can return ERR_EMPTY_RESPONSE.
    try:
        server = GurukulServer(("127.0.0.1", PORT), Handler)
    except OSError as err:
        print(
            f"ERROR: port {PORT} already in use ({err}).\n"
            "Purane python/http.server ko Ctrl+C ya yeh chalao:\n"
            f"  Get-NetTCPConnection -LocalPort {PORT} | "
            "%{ Stop-Process -Id $_.OwningProcess -Force }",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"GenAI Gurukul  http://127.0.0.1:{PORT}/genai-gurukul/")
    print("Windows: 127.0.0.1 use karo, localhost (::1) nahi.")
    print("Ask Gurukul chat uses Cursor SDK (local agent, no file edits requested).")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
