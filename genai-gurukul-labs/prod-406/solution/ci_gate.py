"""PROD 406 — CI regression-eval gate (solution).

Fail-closed ship gate for prompt/model candidates. Extends PROD 401 mindset with
optional trace-quality signals when offline eval looks flat but traces worsen.
"""

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
    """CI gate: offline metrics + optional trace worsen checks.

    Higher-is-better for ``required_metrics`` (default: intersection of keys).
    For ``trace_metrics`` (e.g. ``tool_error_rate``, ``p95_latency_ms``),
    *lower* is better — gate fails if candidate rises by more than
    ``max_trace_worsen`` (absolute).
    """
    if max_drop <= 0:
        raise ValueError("max_drop must be positive")
    if max_trace_worsen <= 0:
        raise ValueError("max_trace_worsen must be positive")
    if not isinstance(baseline, Mapping) or not isinstance(candidate, Mapping):
        raise TypeError("baseline and candidate must be mappings")

    if required_metrics is None:
        quality_keys = sorted(set(baseline) & set(candidate))
        if trace_metrics:
            quality_keys = [k for k in quality_keys if k not in set(trace_metrics)]
    else:
        quality_keys = [str(m) for m in required_metrics]

    trace_keys = [str(m) for m in (trace_metrics or [])]

    missing: list[str] = []
    failed: list[str] = []
    drops: dict[str, float] = {}
    trace_deltas: dict[str, float] = {}

    for m in quality_keys:
        if m not in baseline or m not in candidate:
            missing.append(m)
            failed.append(m)
            continue
        drop = float(baseline[m]) - float(candidate[m])
        drops[m] = drop
        if drop > max_drop:
            failed.append(m)

    for m in trace_keys:
        if m not in baseline or m not in candidate:
            missing.append(m)
            failed.append(m)
            continue
        # lower is better — positive delta means worsen
        delta = float(candidate[m]) - float(baseline[m])
        trace_deltas[m] = delta
        if delta > max_trace_worsen:
            failed.append(m)

    passed = len(failed) == 0 and (len(quality_keys) + len(trace_keys)) > 0
    if not quality_keys and not trace_keys:
        passed = False
        missing = missing or ["<no_metrics>"]

    return {
        "passed": passed,
        "failed_metrics": failed,
        "missing_metrics": missing,
        "drops": drops,
        "trace_deltas": trace_deltas,
        "max_drop": float(max_drop),
        "max_trace_worsen": float(max_trace_worsen),
        "checked_quality": list(quality_keys),
        "checked_trace": list(trace_keys),
        "ci_annotation": (
            "PASS: candidate within gates"
            if passed
            else f"FAIL: regression on [{', '.join(failed) or 'unknown'}]"
        ),
    }
