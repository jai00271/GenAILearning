"""PROD 405 — TTFT vs total latency budgets (starter)."""

from __future__ import annotations

from typing import Mapping, Sequence


def check_latency_budgets(
    samples: Sequence[Mapping[str, float]],
    *,
    ttft_budget_ms: float,
    total_budget_ms: float,
    p_threshold: float = 0.95,
) -> dict[str, object]:
    # TODO: separate TTFT vs total gates; return passed + per-budget stats
    raise NotImplementedError("TODO: check_latency_budgets")
