"""PROD 404 — agent cost / tool-loop circuit breaker (starter)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CircuitBreaker:
    max_tool_calls: int = 8
    max_steps: int = 12
    max_usd: float = 0.05
    tool_calls: int = 0
    steps: int = 0
    usd: float = 0.0
    open: bool = False
    trip_reason: str | None = None
    events: list[dict] = field(default_factory=list)

    def note_step(self, usd_delta: float = 0.0) -> dict[str, object]:
        # TODO: meter step; trip on max_steps / max_usd
        raise NotImplementedError("TODO: note_step")

    def note_tool_call(self, *, usd_delta: float = 0.0) -> dict[str, object]:
        # TODO: meter tool; trip on max_tool_calls / max_usd
        raise NotImplementedError("TODO: note_tool_call")

    def reset(self) -> None:
        raise NotImplementedError("TODO: reset")


def run_with_breaker(
    actions: list[tuple[str, float]],
    *,
    max_tool_calls: int = 8,
    max_steps: int = 12,
    max_usd: float = 0.05,
) -> dict[str, object]:
    # TODO: drive CircuitBreaker over actions; return halted summary
    raise NotImplementedError("TODO: run_with_breaker")


def guard_callable(
    fn: Callable[[], object],
    breaker: CircuitBreaker,
    *,
    kind: str = "step",
    usd_delta: float = 0.0,
) -> object:
    raise NotImplementedError("TODO: guard_callable")
