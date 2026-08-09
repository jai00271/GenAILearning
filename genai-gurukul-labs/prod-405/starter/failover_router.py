"""PROD 405 — multi-provider failover router (starter)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence


@dataclass
class ProviderResult:
    provider: str
    ok: bool
    text: str = ""
    error: str | None = None
    timed_out: bool = False
    ttft_ms: float | None = None
    total_ms: float | None = None


@dataclass
class FailoverRouter:
    providers: Sequence[str]
    call_fn: Callable[[str, float], ProviderResult]
    mid_stream_timeout_ms: float = 5_000.0
    failure_threshold: int = 2
    _failures: dict[str, int] = field(default_factory=dict)
    _open: set[str] = field(default_factory=set)
    attempts: list[dict] = field(default_factory=list)

    def complete(self, prompt: str = "") -> dict[str, object]:
        # TODO: try providers; skip open; honor mid-stream timeout
        raise NotImplementedError("TODO: FailoverRouter.complete")


def route_with_failover(
    providers: Sequence[str],
    outcomes: Sequence[ProviderResult],
    *,
    mid_stream_timeout_ms: float = 5_000.0,
    failure_threshold: int = 2,
) -> dict[str, object]:
    raise NotImplementedError("TODO: route_with_failover")
