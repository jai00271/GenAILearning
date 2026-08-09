"""Failover stub — secondary path when primary LLM/retriever fails."""

from __future__ import annotations

from typing import Callable


class PrimaryFailure(RuntimeError):
    """Raised by the primary path to exercise failover in demos/tests."""


def complete_with_failover(
    primary: Callable[[str], str],
    secondary: Callable[[str], str],
    prompt: str,
) -> tuple[str, str]:
    """
    Try primary; on any Exception, call secondary.

    Returns (answer, path) where path is \"primary\" or \"failover\".
    """
    try:
        return primary(prompt), "primary"
    except Exception:  # noqa: BLE001 — intentional broad catch for stub
        return secondary(prompt), "failover"


def primary_stub(prompt: str) -> str:
    """Default primary: echo-style draft (replace with real model call)."""
    if prompt.strip().upper().startswith("FORCE_FAIL"):
        raise PrimaryFailure("simulated primary outage")
    return f"[primary] Draft next steps for: {prompt[:200]}"


def secondary_stub(prompt: str) -> str:
    """Degraded path: shorter template answer."""
    return (
        "[failover] Primary model unavailable. "
        f"Check runbook index and page on-call for: {prompt[:120]}"
    )
