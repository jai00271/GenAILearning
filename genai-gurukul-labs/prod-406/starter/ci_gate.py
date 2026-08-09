"""PROD 406 — CI regression-eval gate (starter)."""

from __future__ import annotations

from typing import Mapping, Sequence


def ci_eval_gate(
    baseline: Mapping[str, float],
    candidate: Mapping[str, float],
    *,
    max_drop: float = 0.05,
    required_metrics: Sequence[str] | None = None,
    trace_metrics: Sequence[str] | None = None,
    max_trace_worsen: float = 0.05,
) -> dict[str, object]:
    # TODO: quality max_drop + trace worsen (lower-is-better) gates
    raise NotImplementedError("TODO: ci_eval_gate")
