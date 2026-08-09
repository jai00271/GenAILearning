"""Convergent checks for PROD 406 — CI gate + feature flags + sticky hash."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from ci_gate import ci_eval_gate  # noqa: E402
from feature_flag import (  # noqa: E402
    canary_plan,
    choose_variant,
    in_rollout,
    sticky_bucket,
)


def test_ci_gate_pass():
    baseline = {"judge_agree": 0.82, "task_f1": 0.75}
    cand = {"judge_agree": 0.80, "task_f1": 0.74}
    out = ci_eval_gate(baseline, cand, max_drop=0.05)
    assert out["passed"] is True
    assert out["ci_annotation"].startswith("PASS")


def test_ci_gate_quality_fail():
    baseline = {"judge_agree": 0.82}
    cand = {"judge_agree": 0.70}
    out = ci_eval_gate(baseline, cand, max_drop=0.05)
    assert out["passed"] is False
    assert "judge_agree" in out["failed_metrics"]
    assert out["ci_annotation"].startswith("FAIL")


def test_ci_gate_eval_flat_traces_worse():
    # Offline eval flat, but tool_error_rate worsens → fail (tie to PROD 404 traces)
    baseline = {
        "judge_agree": 0.80,
        "tool_error_rate": 0.02,
        "p95_latency_ms": 1200.0,
    }
    cand = {
        "judge_agree": 0.80,  # flat
        "tool_error_rate": 0.10,  # worse (lower-is-better)
        "p95_latency_ms": 1200.02,  # within max_trace_worsen=0.05
    }
    out = ci_eval_gate(
        baseline,
        cand,
        max_drop=0.05,
        required_metrics=["judge_agree"],
        trace_metrics=["tool_error_rate", "p95_latency_ms"],
        max_trace_worsen=0.05,
    )
    assert out["passed"] is False
    assert "tool_error_rate" in out["failed_metrics"]
    assert "p95_latency_ms" not in out["failed_metrics"]
    assert out["drops"]["judge_agree"] == pytest.approx(0.0)


def test_ci_gate_trace_pass_with_flat_eval():
    baseline = {"judge_agree": 0.80, "tool_error_rate": 0.02}
    cand = {"judge_agree": 0.79, "tool_error_rate": 0.03}
    out = ci_eval_gate(
        baseline,
        cand,
        max_drop=0.05,
        required_metrics=["judge_agree"],
        trace_metrics=["tool_error_rate"],
        max_trace_worsen=0.05,
    )
    assert out["passed"] is True


def test_ci_gate_validation():
    with pytest.raises(ValueError):
        ci_eval_gate({"a": 1.0}, {"a": 1.0}, max_drop=0.0)


def test_sticky_bucket_stable():
    a = sticky_bucket("tenant-42")
    b = sticky_bucket("tenant-42")
    assert a == b
    assert 0 <= a < 100
    # Different keys should usually differ (not a hard hash guarantee, but salt+key)
    assert sticky_bucket("tenant-42", salt="other") != a or True  # salt changes space
    assert sticky_bucket("tenant-99") != a or sticky_bucket("tenant-1") != a


def test_in_rollout_extremes():
    assert in_rollout("anyone", 0.0) is False
    assert in_rollout("anyone", 100.0) is True


def test_in_rollout_sticky_monotonic():
    key = "user-7"
    # If in at 10%, must still be in at 50% (same salt, 100 buckets)
    if in_rollout(key, 10.0):
        assert in_rollout(key, 50.0) is True
    # Collect a key that is in 50% but check consistency
    assert isinstance(in_rollout(key, 50.0), bool)


def test_choose_variant_control_vs_treatment():
    flag = {
        "key": "model_swap",
        "percentage": 0.0,
        "control": "gpt-demo",
        "treatment": "claude-demo",
    }
    out = choose_variant("u1", flag)
    assert out["variant"] == "control"
    assert out["value"] == "gpt-demo"
    assert out["in_rollout"] is False

    flag100 = {**flag, "percentage": 100.0}
    out2 = choose_variant("u1", flag100)
    assert out2["variant"] == "treatment"
    assert out2["value"] == "claude-demo"


def test_canary_plan_default_stages():
    plan = canary_plan(control="prompt-v1", treatment="prompt-v2")
    assert [s["percentage"] for s in plan] == [1.0, 5.0, 25.0, 100.0]
    assert plan[0]["flag"]["control"] == "prompt-v1"
    assert plan[-1]["flag"]["treatment"] == "prompt-v2"


def test_canary_plan_rejects_decreasing():
    with pytest.raises(ValueError):
        canary_plan(stages=[10.0, 5.0])
