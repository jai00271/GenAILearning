"""PROD 405 — multi-provider failover router with mid-stream timeout (solution)."""

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
    """Try providers in order; skip open-circuit ones; honor mid-stream timeout."""

    providers: Sequence[str]
    # Simulated call: (provider, mid_stream_timeout_ms) -> ProviderResult
    call_fn: Callable[[str, float], ProviderResult]
    mid_stream_timeout_ms: float = 5_000.0
    failure_threshold: int = 2
    _failures: dict[str, int] = field(default_factory=dict)
    _open: set[str] = field(default_factory=set)
    attempts: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.providers:
            raise ValueError("providers must be non-empty")
        if self.mid_stream_timeout_ms <= 0:
            raise ValueError("mid_stream_timeout_ms must be positive")
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")

    def _record_failure(self, provider: str, reason: str) -> None:
        self._failures[provider] = self._failures.get(provider, 0) + 1
        if self._failures[provider] >= self.failure_threshold:
            self._open.add(provider)
        self.attempts.append(
            {"provider": provider, "ok": False, "reason": reason, "open": provider in self._open}
        )

    def _record_success(self, provider: str) -> None:
        self._failures[provider] = 0
        self.attempts.append({"provider": provider, "ok": True, "reason": None, "open": False})

    def is_open(self, provider: str) -> bool:
        return provider in self._open

    def complete(self, prompt: str = "") -> dict[str, object]:
        """Run failover until one provider succeeds or all exhausted."""
        _ = prompt  # available for call_fn closures / tracing
        last_error: str | None = None
        for provider in self.providers:
            if provider in self._open:
                self.attempts.append(
                    {
                        "provider": provider,
                        "ok": False,
                        "reason": "circuit_open",
                        "open": True,
                        "skipped": True,
                    }
                )
                continue
            result = self.call_fn(provider, self.mid_stream_timeout_ms)
            if result.timed_out:
                self._record_failure(provider, "mid_stream_timeout")
                last_error = "mid_stream_timeout"
                continue
            if not result.ok:
                self._record_failure(provider, result.error or "provider_error")
                last_error = result.error or "provider_error"
                continue
            self._record_success(provider)
            return {
                "ok": True,
                "provider": provider,
                "text": result.text,
                "ttft_ms": result.ttft_ms,
                "total_ms": result.total_ms,
                "attempts": list(self.attempts),
                "open_providers": sorted(self._open),
            }
        return {
            "ok": False,
            "provider": None,
            "text": "",
            "error": last_error or "all_providers_failed",
            "attempts": list(self.attempts),
            "open_providers": sorted(self._open),
        }


def route_with_failover(
    providers: Sequence[str],
    outcomes: Sequence[ProviderResult],
    *,
    mid_stream_timeout_ms: float = 5_000.0,
    failure_threshold: int = 2,
) -> dict[str, object]:
    """Convenience: map provider → canned outcome (by order of outcomes list).

    ``outcomes`` length should match unique calls attempted; we zip by provider order,
    reusing a dict keyed by provider name when provided as a one-shot map via
    matching provider field.
    """
    by_name: dict[str, ProviderResult] = {}
    for o in outcomes:
        by_name[o.provider] = o

    def call_fn(provider: str, timeout_ms: float) -> ProviderResult:
        if provider not in by_name:
            return ProviderResult(provider=provider, ok=False, error="no_fixture")
        r = by_name[provider]
        # If fixture claims a total above timeout, treat as mid-stream timeout
        if r.total_ms is not None and r.total_ms > timeout_ms:
            return ProviderResult(
                provider=provider,
                ok=False,
                timed_out=True,
                error="mid_stream_timeout",
                ttft_ms=r.ttft_ms,
                total_ms=r.total_ms,
            )
        return r

    router = FailoverRouter(
        providers=providers,
        call_fn=call_fn,
        mid_stream_timeout_ms=mid_stream_timeout_ms,
        failure_threshold=failure_threshold,
    )
    return router.complete()
