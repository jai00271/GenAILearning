"""PROD 401 — regression gate helper (solution).

Ship/no-ship when candidate metrics drop vs a frozen baseline after a prompt
tweak (or any candidate change). Offline, deterministic.
"""

from __future__ import annotations

from typing import Mapping, Sequence


def regression_gate(
    baseline_scores: Mapping[str, float],
    candidate_scores: Mapping[str, float],
    *,
    max_drop: float = 0.05,
    required_metrics: Sequence[str] | None = None,
) -> dict[str, object]:
    """Compare candidate scores to baseline; fail if any required metric drops.

    Parameters
    ----------
    baseline_scores / candidate_scores
        Metric name → float score (higher is better).
    max_drop
        Maximum allowed absolute drop (baseline - candidate). Default 0.05.
        Non-positive max_drop → ValueError.
    required_metrics
        Metrics that must be present and checked. Default: intersection of keys
        that appear in *both* maps. If a required metric is missing from either
        side → gate fails with ``missing_metrics``.

    Returns
    -------
    ``{"passed": bool, "drops": {metric: drop}, "failed_metrics": [...],
      "missing_metrics": [...], "max_drop": float, "improvements": {...}}``
    """
    if max_drop <= 0:
        raise ValueError("max_drop must be positive")
    if not isinstance(baseline_scores, Mapping) or not isinstance(candidate_scores, Mapping):
        raise TypeError("scores must be mappings")

    if required_metrics is None:
        metrics = sorted(set(baseline_scores) & set(candidate_scores))
    else:
        metrics = [str(m) for m in required_metrics]

    missing: list[str] = []
    drops: dict[str, float] = {}
    improvements: dict[str, float] = {}
    failed: list[str] = []

    for m in metrics:
        if m not in baseline_scores or m not in candidate_scores:
            missing.append(m)
            failed.append(m)
            continue
        base = float(baseline_scores[m])
        cand = float(candidate_scores[m])
        drop = base - cand
        drops[m] = float(drop)
        if drop > max_drop:
            failed.append(m)
        elif drop < 0:
            improvements[m] = float(-drop)

    passed = len(failed) == 0 and len(metrics) > 0
    if not metrics:
        # Nothing to check — fail closed (regression mindset)
        passed = False
        missing = missing or ["<no_metrics>"]

    return {
        "passed": passed,
        "drops": drops,
        "failed_metrics": failed,
        "missing_metrics": missing,
        "max_drop": float(max_drop),
        "improvements": improvements,
        "checked_metrics": list(metrics),
    }


def summarize_prompt_tweak_regression(
    baseline_scores: Mapping[str, float],
    candidate_scores: Mapping[str, float],
    *,
    max_drop: float = 0.05,
) -> str:
    """One-line English summary for logs / CI annotations."""
    result = regression_gate(
        baseline_scores,
        candidate_scores,
        max_drop=max_drop,
    )
    if result["passed"]:
        return "PASS: candidate within max_drop of baseline on all checked metrics"
    failed = ", ".join(result["failed_metrics"]) or "unknown"
    return f"FAIL: regression on [{failed}] (max_drop={max_drop})"
