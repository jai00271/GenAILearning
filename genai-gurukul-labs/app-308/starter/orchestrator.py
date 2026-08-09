"""APP 308 — Supervisor + worker multi-agent graph (starter).

Fill in the TODOs. Success:
  GURUKUL_LAB=starter pytest app-308/tests -q
(or compare against solution/).

Pure Python — no langgraph / crewai install. Shared MCP-shaped tool catalog,
simulated graph edges, trajectory merge for the multi-agent eval hook.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


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
    """In-process shared tool catalog — register once, allowlist per worker."""

    def __init__(
        self,
        *,
        _specs: dict[str, ToolSpec] | None = None,
        _handlers: dict[str, ToolHandler] | None = None,
        _allowed: frozenset[str] | None = None,
    ) -> None:
        self._specs = _specs if _specs is not None else {}
        self._handlers = _handlers if _handlers is not None else {}
        self._allowed = _allowed

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        """Register (or replace) a tool. Empty name → ValueError."""
        # TODO: validate name; store spec + handler
        raise NotImplementedError

    def list_tools(self) -> list[ToolSpec]:
        """Return visible ToolSpec list (respect allowlist), sorted by name."""
        # TODO
        raise NotImplementedError

    def list_mcp(self) -> list[dict[str, Any]]:
        """Serialize list_tools() via to_mcp_dict()."""
        # TODO
        raise NotImplementedError

    def call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke handler. Unknown/disallowed → {"ok": False, "error": "unknown_tool", ...}."""
        # TODO
        raise NotImplementedError

    def allowlist(self, names: Iterable[str]) -> SharedToolCatalog:
        """Return a view that shares handlers but only exposes ``names``."""
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Fake offline tools
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
    clipped = raw if len(raw) <= 120 else raw[:117] + "..."
    return {"ok": True, "summary": f"SUMMARY: {clipped}"}


def build_default_catalog() -> SharedToolCatalog:
    """Register search_kb, ticket_lookup, summarize_notes on a fresh catalog."""
    # TODO: construct SharedToolCatalog and register the three tools
    raise NotImplementedError


@dataclass
class TrajectoryEvent:
    seq: int
    agent_id: str
    kind: str
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


def merge_trajectories(events: list[TrajectoryEvent]) -> list[TrajectoryEvent]:
    """Sort by seq ascending (stable)."""
    # TODO
    raise NotImplementedError


def supervisor_node(state: GraphState, catalog: SharedToolCatalog) -> GraphState:
    """Assign pending worker tasks from the goal, or route to merge/end."""
    # TODO: see solution for keyword routing (INC* → ticket worker; vpn/okta/… → research)
    raise NotImplementedError


def worker_ticket_node(state: GraphState, catalog: SharedToolCatalog) -> GraphState:
    """Run ticket_lookup (+ summarize) via allowlisted catalog; return to supervisor."""
    # TODO
    raise NotImplementedError


def worker_research_node(state: GraphState, catalog: SharedToolCatalog) -> GraphState:
    """Run search_kb (+ summarize) via allowlisted catalog; return to supervisor."""
    # TODO
    raise NotImplementedError


def merge_node(state: GraphState) -> GraphState:
    """Merge trajectories + worker_outputs into final_answer; route to end."""
    # TODO
    raise NotImplementedError


def next_edge(state: GraphState) -> str:
    """Return state.node, or 'end' if done."""
    # TODO
    raise NotImplementedError


def run_supervisor_graph(
    goal: str,
    catalog: SharedToolCatalog | None = None,
    *,
    max_hops: int = 12,
) -> dict[str, Any]:
    """Drive supervisor → workers → merge → end. Return dict with trajectory."""
    # TODO
    raise NotImplementedError


def trajectory_eval_summary(trajectory: list[dict[str, Any]] | list[TrajectoryEvent]) -> dict[str, Any]:
    """Counts by agent/kind + tool_names_called from tool_call events."""
    # TODO
    raise NotImplementedError
