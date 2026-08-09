"""APP 308 — Supervisor + worker multi-agent graph (solution).

Pure-Python teaching stand-in for LangGraph / CrewAI-style orchestration.
No langgraph / crewai install required: nodes + conditional edges live in dicts.

Shared ``SharedToolCatalog`` is the MCP-shaped tool surface every agent sees
(allowlisted views per worker). Trajectory events carry ``agent_id`` so an
eval hook can merge multi-agent traces (→ PROD 401 deepens agent eval).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


# ---------------------------------------------------------------------------
# MCP-shaped shared tool catalog
# Spec shape: https://modelcontextprotocol.io/specification/2025-03-26/server/tools
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolSpec:
    """One tool in the shared catalog (MCP Tool subset)."""

    name: str
    description: str
    input_schema: dict[str, Any]

    def to_mcp_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


ToolHandler = Callable[..., dict[str, Any]]


class SharedToolCatalog:
    """In-process shared tool catalog — all agents register once, call by name.

    ``allowlist(names)`` returns a *view* that can only list/call those tools.
    That mirrors giving each worker an MCP server (or filtered tool list)
    without copying handler implementations.
    """

    def __init__(
        self,
        *,
        _specs: dict[str, ToolSpec] | None = None,
        _handlers: dict[str, ToolHandler] | None = None,
        _allowed: frozenset[str] | None = None,
    ) -> None:
        self._specs = _specs if _specs is not None else {}
        self._handlers = _handlers if _handlers is not None else {}
        self._allowed = _allowed  # None → all registered names

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        """Register (or replace) a tool. Empty name → ValueError."""
        if not spec.name or not str(spec.name).strip():
            raise ValueError("tool name must be non-empty")
        self._specs[spec.name] = spec
        self._handlers[spec.name] = handler

    def _visible_names(self) -> list[str]:
        names = sorted(self._specs)
        if self._allowed is None:
            return names
        return [n for n in names if n in self._allowed]

    def list_tools(self) -> list[ToolSpec]:
        """tools/list — descriptors visible to this catalog/view."""
        return [self._specs[n] for n in self._visible_names()]

    def list_mcp(self) -> list[dict[str, Any]]:
        """tools/list serialized to MCP dicts."""
        return [s.to_mcp_dict() for s in self.list_tools()]

    def call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """tools/call — unknown or disallowed tool → structured error (no raise)."""
        args = dict(arguments or {})
        if name not in self._specs or (
            self._allowed is not None and name not in self._allowed
        ):
            return {"ok": False, "error": "unknown_tool", "name": name}
        try:
            return self._handlers[name](**args)
        except TypeError as exc:
            return {"ok": False, "error": "bad_arguments", "name": name, "detail": str(exc)}
        except Exception as exc:  # noqa: BLE001 — keep graph alive
            return {"ok": False, "error": "tool_exception", "name": name, "detail": str(exc)}

    def allowlist(self, names: Iterable[str]) -> SharedToolCatalog:
        """Return a view restricted to ``names`` (shared underlying handlers)."""
        allowed = frozenset(str(n) for n in names)
        return SharedToolCatalog(
            _specs=self._specs,
            _handlers=self._handlers,
            _allowed=allowed,
        )


# ---------------------------------------------------------------------------
# Fake offline tools (IT ops flavor — same world as APP 307)
# ---------------------------------------------------------------------------

_KB: dict[str, str] = {
    "vpn": "Split-tunnel VPN drops often mean DNS suffix misconfig; check GlobalProtect profile.",
    "okta": "Okta MFA push timeout: verify Factor sequencing and network to Okta agents.",
    "leave": "HR leave balance mismatches: re-sync Workday → portal nightly job.",
}

_TICKETS: dict[str, dict[str, Any]] = {
    "INC1001": {
        "id": "INC1001",
        "status": "in_progress",
        "summary": "VPN disconnects on split-tunnel",
        "assignee": "netops",
    },
    "INC1002": {
        "id": "INC1002",
        "status": "resolved",
        "summary": "Okta MFA push timeout",
        "assignee": "iam",
    },
}


def search_kb(query: str) -> dict[str, Any]:
    q = str(query).strip().lower()
    hits = []
    for key, text in _KB.items():
        if key in q or any(tok in text.lower() for tok in q.split() if len(tok) > 3):
            hits.append({"id": key, "snippet": text})
    if not hits and q:
        # fallback: return all keys as weak hits for offline demos
        hits = [{"id": k, "snippet": v} for k, v in _KB.items()][:1]
    return {"ok": True, "query": query, "hits": hits}


def ticket_lookup(ticket_id: str) -> dict[str, Any]:
    tid = str(ticket_id).strip().upper()
    row = _TICKETS.get(tid)
    if row is None:
        return {"ok": False, "ticket_id": tid, "error": "not_found"}
    return {"ok": True, "ticket": dict(row)}


def summarize_notes(text: str) -> dict[str, Any]:
    raw = str(text).strip()
    if not raw:
        return {"ok": False, "error": "empty_notes"}
    # Deterministic toy "summary"
    clipped = raw if len(raw) <= 120 else raw[:117] + "..."
    return {"ok": True, "summary": f"SUMMARY: {clipped}"}


def build_default_catalog() -> SharedToolCatalog:
    """Shared catalog every agent starts from (MCP across agents)."""
    cat = SharedToolCatalog()
    cat.register(
        ToolSpec(
            name="search_kb",
            description="Search the offline ops knowledge base by free-text query.",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
        ),
        lambda **kw: search_kb(str(kw.get("query", ""))),
    )
    cat.register(
        ToolSpec(
            name="ticket_lookup",
            description="Look up an ITSM ticket by id (e.g. INC1001).",
            input_schema={
                "type": "object",
                "properties": {"ticket_id": {"type": "string"}},
                "required": ["ticket_id"],
                "additionalProperties": False,
            },
        ),
        lambda **kw: ticket_lookup(str(kw.get("ticket_id", ""))),
    )
    cat.register(
        ToolSpec(
            name="summarize_notes",
            description="Summarize free-text notes into a short SUMMARY line.",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
        ),
        lambda **kw: summarize_notes(str(kw.get("text", ""))),
    )
    return cat


# ---------------------------------------------------------------------------
# Trajectory + graph state
# ---------------------------------------------------------------------------


@dataclass
class TrajectoryEvent:
    """One multi-agent trajectory beat (eval hook — not Recall@k)."""

    seq: int
    agent_id: str
    kind: str  # route | tool_call | tool_result | message | merge | halt
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "agent_id": self.agent_id,
            "kind": self.kind,
            "detail": dict(self.detail),
        }


@dataclass
class GraphState:
    """Mutable state passed along simulated graph edges."""

    goal: str
    node: str = "supervisor"
    pending: list[dict[str, Any]] = field(default_factory=list)
    worker_outputs: dict[str, str] = field(default_factory=dict)
    events: list[TrajectoryEvent] = field(default_factory=list)
    hop: int = 0
    done: bool = False
    final_answer: str | None = None
    _seq: int = 0

    def emit(self, agent_id: str, kind: str, detail: dict[str, Any] | None = None) -> None:
        self._seq += 1
        self.events.append(
            TrajectoryEvent(
                seq=self._seq,
                agent_id=agent_id,
                kind=kind,
                detail=dict(detail or {}),
            )
        )


# ---------------------------------------------------------------------------
# Nodes (pure functions mutating GraphState)
# ---------------------------------------------------------------------------


def _extract_ticket_id(goal: str) -> str | None:
    import re

    m = re.search(r"INC\d+", goal.upper())
    return m.group(0) if m else None


def supervisor_node(state: GraphState, catalog: SharedToolCatalog) -> GraphState:
    """Route work to workers or finish. Uses catalog list only (no side tools)."""
    tools = [t.name for t in catalog.list_tools()]
    state.emit(
        "supervisor",
        "message",
        {"event": "supervise", "goal": state.goal, "catalog_tools": tools},
    )

    # Already have outputs → merge
    need_ticket = _extract_ticket_id(state.goal) is not None
    need_research = any(
        k in state.goal.lower() for k in ("vpn", "okta", "leave", "policy", "kb", "how")
    )
    # Default: if neither keyword, still do a light research pass on the goal
    if not need_ticket and not need_research:
        need_research = True

    if "ticket" not in state.worker_outputs and need_ticket:
        state.pending.append(
            {
                "worker_id": "worker_ticket",
                "instruction": f"Lookup ticket for: {state.goal}",
                "tools": ["ticket_lookup", "summarize_notes"],
            }
        )
    if "research" not in state.worker_outputs and need_research:
        state.pending.append(
            {
                "worker_id": "worker_research",
                "instruction": f"Search KB for: {state.goal}",
                "tools": ["search_kb", "summarize_notes"],
            }
        )

    if state.pending:
        nxt = state.pending[0]["worker_id"]
        state.emit("supervisor", "route", {"to": nxt, "pending": len(state.pending)})
        state.node = nxt
        return state

    # Nothing pending — go merge if we have any outputs, else end with echo
    if state.worker_outputs:
        state.emit("supervisor", "route", {"to": "merge"})
        state.node = "merge"
    else:
        state.final_answer = f"No workers needed. Echo: {state.goal}"
        state.emit("supervisor", "message", {"final": state.final_answer})
        state.node = "end"
        state.done = True
    return state


def worker_ticket_node(state: GraphState, catalog: SharedToolCatalog) -> GraphState:
    """Ticket worker — allowlisted tools only."""
    return _run_worker(
        state,
        worker_id="worker_ticket",
        output_key="ticket",
        catalog=catalog,
        tool_plan=_ticket_plan,
    )


def worker_research_node(state: GraphState, catalog: SharedToolCatalog) -> GraphState:
    """Research worker — KB search + summarize."""
    return _run_worker(
        state,
        worker_id="worker_research",
        output_key="research",
        catalog=catalog,
        tool_plan=_research_plan,
    )


def _ticket_plan(goal: str) -> list[tuple[str, dict[str, Any]]]:
    tid = _extract_ticket_id(goal) or "INC1001"
    return [
        ("ticket_lookup", {"ticket_id": tid}),
        ("summarize_notes", {"text": f"ticket {tid} lookup for goal={goal}"}),
    ]


def _research_plan(goal: str) -> list[tuple[str, dict[str, Any]]]:
    return [
        ("search_kb", {"query": goal}),
        ("summarize_notes", {"text": f"research notes for: {goal}"}),
    ]


def _run_worker(
    state: GraphState,
    *,
    worker_id: str,
    output_key: str,
    catalog: SharedToolCatalog,
    tool_plan: Callable[[str], list[tuple[str, dict[str, Any]]]],
) -> GraphState:
    # Pop matching pending task (or synthesize)
    task = None
    rest: list[dict[str, Any]] = []
    for p in state.pending:
        if task is None and p.get("worker_id") == worker_id:
            task = p
        else:
            rest.append(p)
    state.pending = rest

    allowed = list(task["tools"]) if task else ["summarize_notes"]
    view = catalog.allowlist(allowed)
    state.emit(
        worker_id,
        "message",
        {
            "event": "start",
            "allowed_tools": [t.name for t in view.list_tools()],
            "instruction": (task or {}).get("instruction", state.goal),
        },
    )

    bits: list[str] = []
    for name, args in tool_plan(state.goal):
        state.emit(worker_id, "tool_call", {"name": name, "arguments": dict(args)})
        result = view.call(name, args)
        ok = bool(result.get("ok", False)) if "ok" in result else "error" not in result
        state.emit(
            worker_id,
            "tool_result" if ok else "tool_result",
            {"name": name, "result": result, "ok": ok},
        )
        bits.append(str(result))

    summary = " | ".join(bits) if bits else "(no tools)"
    state.worker_outputs[output_key] = summary
    state.emit(worker_id, "message", {"event": "done", "output_key": output_key})
    state.emit(worker_id, "route", {"to": "supervisor"})
    state.node = "supervisor"
    return state


def merge_node(state: GraphState) -> GraphState:
    """Merge worker outputs + trajectory into a final answer."""
    merged_events = merge_trajectories(state.events)
    state.events = merged_events
    parts = [f"{k}: {v}" for k, v in sorted(state.worker_outputs.items())]
    answer = "MERGED: " + " || ".join(parts) if parts else "MERGED: (empty)"
    state.final_answer = answer
    state.emit(
        "merge",
        "merge",
        {
            "workers": sorted(state.worker_outputs),
            "n_events": len(state.events),
            "final": answer,
        },
    )
    state.emit("merge", "route", {"to": "end"})
    state.node = "end"
    state.done = True
    return state


# ---------------------------------------------------------------------------
# Edges + runner (LangGraph-shaped, no dependency)
# ---------------------------------------------------------------------------

# node name → callable
NodeFn = Callable[..., GraphState]


def merge_trajectories(events: list[TrajectoryEvent]) -> list[TrajectoryEvent]:
    """Sort events by ``seq`` ascending (stable). Idempotent for already-ordered."""
    return sorted(events, key=lambda e: (e.seq, e.agent_id, e.kind))


def next_edge(state: GraphState) -> str:
    """Conditional edge function — returns the next node name."""
    if state.done or state.node == "end":
        return "end"
    return state.node


def run_supervisor_graph(
    goal: str,
    catalog: SharedToolCatalog | None = None,
    *,
    max_hops: int = 12,
) -> dict[str, Any]:
    """Run supervisor→workers→merge→end until done or ``max_hops``.

    Returns a JSON-friendly dict: final_answer, path, trajectory, halted, hops.
    """
    if max_hops < 1:
        raise ValueError("max_hops must be >= 1")
    if not str(goal).strip():
        raise ValueError("goal must be non-empty")

    cat = catalog if catalog is not None else build_default_catalog()
    state = GraphState(goal=str(goal).strip())
    path: list[str] = []

    nodes: dict[str, NodeFn] = {
        "supervisor": lambda s: supervisor_node(s, cat),
        "worker_ticket": lambda s: worker_ticket_node(s, cat),
        "worker_research": lambda s: worker_research_node(s, cat),
        "merge": lambda s: merge_node(s),
    }

    while not state.done and state.hop < max_hops:
        state.hop += 1
        node = next_edge(state)
        path.append(node)
        if node == "end":
            state.done = True
            break
        fn = nodes.get(node)
        if fn is None:
            state.emit("graph", "halt", {"reason": "unknown_node", "node": node})
            break
        state = fn(state)

    halted = not state.done or state.final_answer is None
    if state.hop >= max_hops and not state.done:
        state.emit("graph", "halt", {"reason": "max_hops", "max_hops": max_hops})
        halted = True

    return {
        "final_answer": state.final_answer,
        "path": path,
        "trajectory": [e.to_dict() for e in merge_trajectories(state.events)],
        "worker_outputs": dict(state.worker_outputs),
        "halted": halted and state.final_answer is None,
        "hops": state.hop,
    }


def trajectory_eval_summary(trajectory: list[dict[str, Any]] | list[TrajectoryEvent]) -> dict[str, Any]:
    """Eval beat: per-agent counts + tool names across the merged trajectory."""
    events: list[dict[str, Any]] = []
    for e in trajectory:
        if isinstance(e, TrajectoryEvent):
            events.append(e.to_dict())
        else:
            events.append(dict(e))

    by_agent: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    tools: list[str] = []
    for e in events:
        aid = str(e.get("agent_id", ""))
        kind = str(e.get("kind", ""))
        by_agent[aid] = by_agent.get(aid, 0) + 1
        by_kind[kind] = by_kind.get(kind, 0) + 1
        if kind == "tool_call":
            name = (e.get("detail") or {}).get("name")
            if name:
                tools.append(str(name))

    return {
        "n_events": len(events),
        "counts_by_agent": by_agent,
        "counts_by_kind": by_kind,
        "tool_names_called": tools,
        "agents_seen": sorted(by_agent),
    }
