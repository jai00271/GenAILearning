"""PROD 404 — agent cost / tool-loop circuit breaker (solution).

Hard-halts runaway agent loops. Complements Debug Lab B (soft budget only logged).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CircuitBreaker:
    """Trip when tool calls, steps, or USD exceed hard limits."""

    max_tool_calls: int = 8
    max_steps: int = 12
    max_usd: float = 0.05
    tool_calls: int = 0
    steps: int = 0
    usd: float = 0.0
    open: bool = False
    trip_reason: str | None = None
    events: list[dict] = field(default_factory=list)

    def _trip(self, reason: str) -> None:
        self.open = True
        self.trip_reason = reason
        self.events.append({"kind": "circuit_open", "reason": reason})

    def note_step(self, usd_delta: float = 0.0) -> dict[str, object]:
        """Record one agent step (LLM turn). Raises RuntimeError if already open."""
        if self.open:
            raise RuntimeError(f"circuit open: {self.trip_reason}")
        self.steps += 1
        self.usd += float(usd_delta)
        self.events.append(
            {"kind": "step", "steps": self.steps, "usd": round(self.usd, 8)}
        )
        if self.steps > self.max_steps:
            self._trip("max_steps")
            raise RuntimeError("circuit open: max_steps")
        if self.usd > self.max_usd:
            self._trip("max_usd")
            raise RuntimeError("circuit open: max_usd")
        return {"ok": True, "steps": self.steps, "usd": round(self.usd, 8)}

    def note_tool_call(self, *, usd_delta: float = 0.0) -> dict[str, object]:
        """Record one tool invocation; trip on max_tool_calls / max_usd."""
        if self.open:
            raise RuntimeError(f"circuit open: {self.trip_reason}")
        self.tool_calls += 1
        self.usd += float(usd_delta)
        self.events.append(
            {
                "kind": "tool",
                "tool_calls": self.tool_calls,
                "usd": round(self.usd, 8),
            }
        )
        if self.tool_calls > self.max_tool_calls:
            self._trip("max_tool_calls")
            raise RuntimeError("circuit open: max_tool_calls")
        if self.usd > self.max_usd:
            self._trip("max_usd")
            raise RuntimeError("circuit open: max_usd")
        return {
            "ok": True,
            "tool_calls": self.tool_calls,
            "usd": round(self.usd, 8),
        }

    def reset(self) -> None:
        self.tool_calls = 0
        self.steps = 0
        self.usd = 0.0
        self.open = False
        self.trip_reason = None
        self.events.clear()


def run_with_breaker(
    actions: list[tuple[str, float]],
    *,
    max_tool_calls: int = 8,
    max_steps: int = 12,
    max_usd: float = 0.05,
) -> dict[str, object]:
    """Simulate a sequence of ('step'|'tool', usd_delta) under a breaker.

    Returns summary with halted=True when the circuit trips mid-run.
    """
    breaker = CircuitBreaker(
        max_tool_calls=max_tool_calls,
        max_steps=max_steps,
        max_usd=max_usd,
    )
    completed = 0
    for kind, delta in actions:
        try:
            if kind == "step":
                breaker.note_step(usd_delta=delta)
            elif kind == "tool":
                breaker.note_tool_call(usd_delta=delta)
            else:
                raise ValueError(f"unknown action kind: {kind}")
            completed += 1
        except RuntimeError:
            return {
                "halted": True,
                "completed": completed,
                "open": True,
                "trip_reason": breaker.trip_reason,
                "tool_calls": breaker.tool_calls,
                "steps": breaker.steps,
                "usd": round(breaker.usd, 8),
                "events": list(breaker.events),
            }
    return {
        "halted": False,
        "completed": completed,
        "open": False,
        "trip_reason": None,
        "tool_calls": breaker.tool_calls,
        "steps": breaker.steps,
        "usd": round(breaker.usd, 8),
        "events": list(breaker.events),
    }


def guard_callable(
    fn: Callable[[], object],
    breaker: CircuitBreaker,
    *,
    kind: str = "step",
    usd_delta: float = 0.0,
) -> object:
    """Execute fn only if breaker allows; meter afterward."""
    if breaker.open:
        raise RuntimeError(f"circuit open: {breaker.trip_reason}")
    result = fn()
    if kind == "tool":
        breaker.note_tool_call(usd_delta=usd_delta)
    else:
        breaker.note_step(usd_delta=usd_delta)
    return result
