"""APP 307 — ReAct agent loop, MCP-style tools, trajectory logging (solution).

Offline teaching stack: FakeLLM emits tool_calls; ToyMCPClient lists/calls tools
via MCP-shaped descriptors (name, description, JSON Schema params). Max-steps
circuit breaker + trajectory log — agents are not scored with RAG metrics alone.
Full agent-eval methodology deepens in PROD 401.
"""

from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


# ---------------------------------------------------------------------------
# MCP-shaped tool descriptor (subset of tools/list Tool schema)
# Spec: https://modelcontextprotocol.io/specification/2025-03-26/server/tools
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolDescriptor:
    """Minimal MCP-style tool descriptor.

    Maps to MCP Tool fields: ``name``, ``description``, ``inputSchema``.
    Lab uses ``input_schema`` as the Python attribute name.
    """

    name: str
    description: str
    input_schema: dict[str, Any]

    def to_mcp_dict(self) -> dict[str, Any]:
        """Serialize to MCP tools/list entry shape."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


@dataclass(frozen=True)
class ToolCall:
    """One model-requested tool invocation (OpenAI/Anthropic-style stand-in)."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LLMResponse:
    """FakeLLM turn: either final text or one-or-more tool calls."""

    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


@dataclass
class TrajectoryStep:
    """One logged beat in the agent loop (eval hook — not Recall@k)."""

    step: int
    kind: str  # "thought" | "tool_call" | "tool_result" | "final" | "error" | "halt"
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Outcome of ``run_react`` including the full trajectory."""

    final_answer: str | None
    trajectory: list[TrajectoryStep]
    halted: bool
    halt_reason: str | None = None
    steps_used: int = 0


class Completer(Protocol):
    """Injectable LLM: returns structured responses given message history."""

    def complete(self, messages: list[dict[str, Any]]) -> LLMResponse:
        ...


# ---------------------------------------------------------------------------
# Injectable tools — calculator + fake ticket lookup
# ---------------------------------------------------------------------------

_BINOPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARYOPS: dict[type, Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_arith(node: ast.AST) -> float | int:
    """Safe arithmetic eval over a restricted AST (no names / calls)."""
    if isinstance(node, ast.Expression):
        return _eval_arith(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_eval_arith(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        left = _eval_arith(node.left)
        right = _eval_arith(node.right)
        return _BINOPS[type(node.op)](left, right)
    raise ValueError("only arithmetic expressions allowed")


def calculator(expression: str) -> dict[str, Any]:
    """Evaluate a simple arithmetic expression string. Returns value or error."""
    try:
        tree = ast.parse(str(expression).strip(), mode="eval")
        value = _eval_arith(tree)
        return {"ok": True, "expression": expression, "value": value}
    except Exception as exc:  # noqa: BLE001 — surface tool error into trajectory
        return {"ok": False, "expression": expression, "error": str(exc)}


# Fake ITSM ticket store (offline)
_TICKETS: dict[str, dict[str, Any]] = {
    "INC1001": {
        "id": "INC1001",
        "status": "in_progress",
        "summary": "VPN disconnects on split-tunnel",
        "assignee": "netops",
        "priority": 2,
    },
    "INC1002": {
        "id": "INC1002",
        "status": "resolved",
        "summary": "Okta MFA push timeout",
        "assignee": "iam",
        "priority": 3,
    },
    "INC1003": {
        "id": "INC1003",
        "status": "open",
        "summary": "Leave balance mismatch in HR portal",
        "assignee": "hris",
        "priority": 4,
    },
}


def ticket_lookup(ticket_id: str) -> dict[str, Any]:
    """Look up a fake ticket by id. Missing id → structured miss (not exception)."""
    tid = str(ticket_id).strip().upper()
    row = _TICKETS.get(tid)
    if row is None:
        return {"ok": False, "ticket_id": tid, "error": "not_found"}
    return {"ok": True, "ticket": dict(row)}


CALCULATOR_DESCRIPTOR = ToolDescriptor(
    name="calculator",
    description="Evaluate a basic arithmetic expression (+ - * / ** // % and parentheses).",
    input_schema={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Arithmetic expression, e.g. '(2+3)*4'",
            }
        },
        "required": ["expression"],
        "additionalProperties": False,
    },
)

TICKET_LOOKUP_DESCRIPTOR = ToolDescriptor(
    name="ticket_lookup",
    description="Look up an ITSM ticket by id (e.g. INC1001). Returns status and summary.",
    input_schema={
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "Ticket identifier such as INC1001",
            }
        },
        "required": ["ticket_id"],
        "additionalProperties": False,
    },
)


ToolHandler = Callable[..., dict[str, Any]]


def default_tool_handlers() -> dict[str, ToolHandler]:
    """Name → callable for the two lab tools."""
    return {
        "calculator": lambda **kwargs: calculator(str(kwargs.get("expression", ""))),
        "ticket_lookup": lambda **kwargs: ticket_lookup(str(kwargs.get("ticket_id", ""))),
    }


def default_tool_descriptors() -> list[ToolDescriptor]:
    return [CALCULATOR_DESCRIPTOR, TICKET_LOOKUP_DESCRIPTOR]


# ---------------------------------------------------------------------------
# Toy MCP client — list / call (offline, in-process)
# ---------------------------------------------------------------------------


class ToyMCPClient:
    """In-process stand-in for an MCP client talking to a tools-capable server.

    Mirrors ``tools/list`` and ``tools/call`` from the MCP tools specification.
    Not a network transport — descriptors + handlers live in-process for pytest.
    """

    def __init__(
        self,
        descriptors: list[ToolDescriptor] | None = None,
        handlers: dict[str, ToolHandler] | None = None,
    ) -> None:
        self._descriptors = {
            d.name: d for d in (descriptors if descriptors is not None else default_tool_descriptors())
        }
        self._handlers = dict(handlers if handlers is not None else default_tool_handlers())

    def list_tools(self) -> list[ToolDescriptor]:
        """MCP tools/list — return registered descriptors (stable name order)."""
        return [self._descriptors[k] for k in sorted(self._descriptors)]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """MCP tools/call — invoke handler; unknown tool → structured error."""
        args = dict(arguments or {})
        if name not in self._handlers:
            return {"ok": False, "error": "unknown_tool", "name": name}
        try:
            return self._handlers[name](**args)
        except TypeError as exc:
            return {"ok": False, "error": "bad_arguments", "name": name, "detail": str(exc)}
        except Exception as exc:  # noqa: BLE001 — keep loop alive; log in trajectory
            return {"ok": False, "error": "tool_exception", "name": name, "detail": str(exc)}


# ---------------------------------------------------------------------------
# FakeLLM — scripted / pattern-driven tool_calls (offline)
# ---------------------------------------------------------------------------


class FakeLLM:
    """Deterministic completer for labs.

    Provide an explicit ``script`` of ``LLMResponse`` objects (consumed in order),
    or leave script empty to use a tiny heuristic that emits calculator /
    ticket_lookup tool_calls from the last user message, then a final answer.
    """

    def __init__(self, script: list[LLMResponse] | None = None) -> None:
        self._script = list(script or [])
        self._i = 0
        self._auto_phase = 0  # 0=maybe tool, 1=final

    def complete(self, messages: list[dict[str, Any]]) -> LLMResponse:
        if self._script:
            if self._i >= len(self._script):
                return LLMResponse(content="(script exhausted)")
            resp = self._script[self._i]
            self._i += 1
            return resp

        # Heuristic path for demos without an explicit script
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = str(m.get("content", ""))
                break

        if self._auto_phase == 0:
            self._auto_phase = 1
            upper = last_user.upper()
            if "INC" in upper:
                # pull first INC####-like token
                m = re.search(r"INC\d+", upper)
                tid = m.group(0) if m else "INC1001"
                return LLMResponse(
                    tool_calls=(
                        ToolCall(id="call_ticket", name="ticket_lookup", arguments={"ticket_id": tid}),
                    )
                )
            if any(ch.isdigit() for ch in last_user) and any(op in last_user for op in "+-*/"):
                # crude: take substring after 'compute' or whole message as expression
                expr = last_user
                for marker in ("compute", "calculate", "what is", "eval"):
                    idx = last_user.lower().find(marker)
                    if idx >= 0:
                        expr = last_user[idx + len(marker) :].strip(" :?")
                        break
                return LLMResponse(
                    tool_calls=(
                        ToolCall(id="call_calc", name="calculator", arguments={"expression": expr}),
                    )
                )
            return LLMResponse(content=f"No tool needed. Echo: {last_user}")

        # After tool results in history, produce a final answer
        tool_bits = [str(m.get("content")) for m in messages if m.get("role") == "tool"]
        summary = tool_bits[-1] if tool_bits else "{}"
        return LLMResponse(content=f"Based on tools: {summary}")


# ---------------------------------------------------------------------------
# ReAct loop — Thought / Action / Observation + max-steps breaker
# ---------------------------------------------------------------------------


def run_react(
    user_message: str,
    *,
    llm: Completer,
    mcp: ToyMCPClient,
    max_steps: int = 6,
    system_prompt: str | None = None,
) -> AgentResult:
    """Run a minimal ReAct-style loop with trajectory logging.

    Each *step* is one LLM completion. If the model returns tool_calls, the
    loop executes them via ``mcp.call_tool``, appends tool results, and
    continues. If ``content`` is set without tool_calls, that is the final
    answer. Exceeding ``max_steps`` sets ``halted=True`` (circuit breaker).

    Errors from tools are recorded as trajectory steps with kind ``error`` /
    failed tool_result — the loop does not crash on a single bad call.
    """
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")

    trajectory: list[TrajectoryStep] = []
    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    tools_catalog = [d.to_mcp_dict() for d in mcp.list_tools()]
    trajectory.append(
        TrajectoryStep(
            step=0,
            kind="thought",
            detail={"event": "start", "tools": [t["name"] for t in tools_catalog]},
        )
    )

    for step in range(1, max_steps + 1):
        try:
            response = llm.complete(messages)
        except Exception as exc:  # noqa: BLE001
            trajectory.append(
                TrajectoryStep(step=step, kind="error", detail={"where": "llm", "error": str(exc)})
            )
            return AgentResult(
                final_answer=None,
                trajectory=trajectory,
                halted=True,
                halt_reason=f"llm_error: {exc}",
                steps_used=step,
            )

        if response.has_tool_calls:
            # Log assistant tool request
            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments},
                    }
                    for tc in response.tool_calls
                ],
            }
            messages.append(assistant_msg)
            trajectory.append(
                TrajectoryStep(
                    step=step,
                    kind="tool_call",
                    detail={
                        "calls": [
                            {"id": tc.id, "name": tc.name, "arguments": dict(tc.arguments)}
                            for tc in response.tool_calls
                        ]
                    },
                )
            )

            for tc in response.tool_calls:
                result = mcp.call_tool(tc.name, tc.arguments)
                if "ok" in result:
                    ok = bool(result["ok"])
                else:
                    ok = "error" not in result
                kind = "tool_result" if ok else "error"
                trajectory.append(
                    TrajectoryStep(
                        step=step,
                        kind=kind,
                        detail={
                            "tool_call_id": tc.id,
                            "name": tc.name,
                            "arguments": dict(tc.arguments),
                            "result": result,
                        },
                    )
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.name,
                        "content": str(result),
                    }
                )
            continue

        # Final answer path
        answer = response.content if response.content is not None else ""
        messages.append({"role": "assistant", "content": answer})
        trajectory.append(
            TrajectoryStep(step=step, kind="final", detail={"content": answer})
        )
        return AgentResult(
            final_answer=answer,
            trajectory=trajectory,
            halted=False,
            halt_reason=None,
            steps_used=step,
        )

    # Circuit breaker
    trajectory.append(
        TrajectoryStep(
            step=max_steps,
            kind="halt",
            detail={"reason": "max_steps", "max_steps": max_steps},
        )
    )
    return AgentResult(
        final_answer=None,
        trajectory=trajectory,
        halted=True,
        halt_reason="max_steps",
        steps_used=max_steps,
    )


def summarize_trajectory(trajectory: list[TrajectoryStep]) -> dict[str, Any]:
    """Eval beat helper: counts for tool-call / error / halt analysis (→ PROD 401)."""
    counts: dict[str, int] = {}
    tool_names: list[str] = []
    for s in trajectory:
        counts[s.kind] = counts.get(s.kind, 0) + 1
        if s.kind == "tool_call":
            for c in s.detail.get("calls", []):
                tool_names.append(str(c.get("name")))
    return {
        "n_steps_logged": len(trajectory),
        "counts_by_kind": counts,
        "tool_names_called": tool_names,
        "had_error": counts.get("error", 0) > 0,
        "hit_max_steps": any(s.kind == "halt" for s in trajectory),
    }
