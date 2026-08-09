"""APP 307 — ReAct agent loop, MCP-style tools, trajectory logging (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest app-307/tests -q
(or compare against solution/).

Offline only — FakeLLM + ToyMCPClient. No paid APIs / LangChain required.
"""

from __future__ import annotations

import ast
import operator
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
        # TODO: return {"name", "description", "inputSchema"}
        raise NotImplementedError


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
    # TODO: parse with ast.parse(..., mode="eval"); return {"ok", "expression", "value"} or error
    raise NotImplementedError


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
    # TODO: normalize id; return ticket dict or {"ok": False, "error": "not_found"}
    raise NotImplementedError


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
        # TODO
        raise NotImplementedError

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """MCP tools/call — invoke handler; unknown tool → structured error."""
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# FakeLLM — scripted tool_calls (offline)
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
        self._auto_phase = 0

    def complete(self, messages: list[dict[str, Any]]) -> LLMResponse:
        # TODO: consume script in order; else heuristic (INC* → ticket_lookup, digits+ops → calculator)
        raise NotImplementedError


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
    """
    # TODO: build messages; loop up to max_steps; log TrajectoryStep list; halt on ceiling
    raise NotImplementedError


def summarize_trajectory(trajectory: list[TrajectoryStep]) -> dict[str, Any]:
    """Eval beat helper: counts for tool-call / error / halt analysis (→ PROD 401)."""
    # TODO: counts_by_kind, tool_names_called, had_error, hit_max_steps
    raise NotImplementedError
