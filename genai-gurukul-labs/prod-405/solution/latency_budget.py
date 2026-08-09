"""PROD 405 — separate TTFT vs total latency budgets (solution)."""

from __future__ import annotations

from typing import Mapping, Sequence


def check_latency_budgets(
    samples: Sequence[Mapping[str, float]],
    *,
    ttft_budget_ms: float,
    total_budget_ms: float,
    p_threshold: float = 0.95,
) -> dict[str, object]:
    """Evaluate TTFT and total-latency budgets independently.

    Each sample needs ``ttft_ms`` and ``total_ms`` (floats, ms).
    ``p_threshold`` is the fraction that must be within budget (e.g. 0.95 ≈ p95 gate).

    Returns per-budget pass/fail plus empirical percentiles.
    """
    if not isinstance(samples, Sequence) or isinstance(samples, (str, bytes)):
        raise TypeError("samples must be a sequence of mappings")
    if ttft_budget_ms <= 0 or total_budget_ms <= 0:
        raise ValueError("budgets must be positive")
    if not (0.0 < p_threshold <= 1.0):
        raise ValueError("p_threshold must be in (0, 1]")
    if len(samples) == 0:
        raise ValueError("samples must be non-empty")

    ttfts: list[float] = []
    totals: list[float] = []
    for i, s in enumerate(samples):
        if not isinstance(s, Mapping):
            raise TypeError(f"sample {i} must be a mapping")
        if "ttft_ms" not in s or "total_ms" not in s:
            raise ValueError(f"sample {i} needs ttft_ms and total_ms")
        ttft = float(s["ttft_ms"])
        total = float(s["total_ms"])
        if ttft < 0 or total < 0:
            raise ValueError("latencies must be non-negative")
        if total < ttft:
            raise ValueError(f"sample {i}: total_ms cannot be < ttft_ms")
        ttfts.append(ttft)
        totals.append(total)

    def pct(xs: list[float], p: float) -> float:
        ordered = sorted(xs)
        # Nearest-rank style for teaching clarity
        idx = min(len(ordered) - 1, max(0, int(round(p * (len(ordered) - 1)))))
        return float(ordered[idx])

    def frac_within(xs: list[float], budget: float) -> float:
        return sum(1 for x in xs if x <= budget) / len(xs)

    ttft_frac = frac_within(ttfts, ttft_budget_ms)
    total_frac = frac_within(totals, total_budget_ms)
    ttft_ok = ttft_frac >= p_threshold
    total_ok = total_frac >= p_threshold

    return {
        "passed": ttft_ok and total_ok,
        "ttft": {
            "budget_ms": float(ttft_budget_ms),
            "frac_within": ttft_frac,
            "p_value_ms": pct(ttfts, p_threshold),
            "passed": ttft_ok,
        },
        "total": {
            "budget_ms": float(total_budget_ms),
            "frac_within": total_frac,
            "p_value_ms": pct(totals, p_threshold),
            "passed": total_ok,
        },
        "n": len(samples),
        "p_threshold": float(p_threshold),
        "failed_budgets": [
            name
            for name, ok in (("ttft", ttft_ok), ("total", total_ok))
            if not ok
        ],
    }
