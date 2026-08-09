"""PROD 401 — regression gate helper (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-401/tests -q
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
    """Fail if any required metric drops more than max_drop vs baseline."""
    # TODO: compute drops; failed_metrics; missing_metrics; passed
    raise NotImplementedError("TODO: regression_gate")


def summarize_prompt_tweak_regression(
    baseline_scores: Mapping[str, float],
    candidate_scores: Mapping[str, float],
    *,
    max_drop: float = 0.05,
) -> str:
    """One-line English summary for logs / CI annotations."""
    # TODO: call regression_gate and format PASS/FAIL string
    raise NotImplementedError("TODO: summarize_prompt_tweak_regression")
