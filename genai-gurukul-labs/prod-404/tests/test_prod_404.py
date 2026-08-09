"""Convergent checks for PROD 404 — cost tracker, circuit breaker, retry storm."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from circuit_breaker import CircuitBreaker, run_with_breaker  # noqa: E402
from cost_tracker import TenantCostTracker  # noqa: E402
from retry_storm import detect_retry_storm  # noqa: E402


def test_cost_tracker_attribution():
    t = TenantCostTracker(hard_budget_usd=1.0, soft_budget_usd=0.01)
    a = t.record("acme", model="gpt-demo", tokens_in=1_000_000, tokens_out=0)
    assert a["usd_charge"] == pytest.approx(2.50)
    assert a["hard_budget_hit"] is True
    assert a["soft_budget_hit"] is True

    t.record("beta", model="claude-demo", tokens_in=0, tokens_out=100_000)
    attr = t.attribution()
    assert set(attr) == {"acme", "beta"}
    assert attr["acme"]["calls"] == 1
    assert attr["beta"]["usd"] == pytest.approx(1.5)
    assert t.total_usd() == pytest.approx(4.0)


def test_cost_tracker_unknown_model():
    t = TenantCostTracker()
    with pytest.raises(KeyError):
        t.record("acme", model="nope", tokens_in=1, tokens_out=0)


def test_cost_tracker_budget_order():
    with pytest.raises(ValueError):
        TenantCostTracker(soft_budget_usd=1.0, hard_budget_usd=0.5)


def test_cost_tracker_bad_tenant():
    t = TenantCostTracker()
    with pytest.raises(TypeError):
        t.record("", model="gpt-demo", tokens_in=1, tokens_out=0)


def test_circuit_trips_on_tool_calls():
    actions = [("tool", 0.001)] * 10
    out = run_with_breaker(actions, max_tool_calls=3, max_steps=100, max_usd=10.0)
    assert out["halted"] is True
    assert out["trip_reason"] == "max_tool_calls"
    assert out["tool_calls"] == 4  # 4th call trips
    assert out["completed"] == 3


def test_circuit_trips_on_usd():
    actions = [("step", 0.02), ("tool", 0.02), ("step", 0.02)]
    out = run_with_breaker(actions, max_tool_calls=50, max_steps=50, max_usd=0.03)
    assert out["halted"] is True
    assert out["trip_reason"] == "max_usd"
    assert out["open"] is True


def test_circuit_trips_on_steps():
    actions = [("step", 0.0)] * 5
    out = run_with_breaker(actions, max_tool_calls=50, max_steps=2, max_usd=10.0)
    assert out["halted"] is True
    assert out["trip_reason"] == "max_steps"
    assert out["steps"] == 3


def test_circuit_completes_under_limits():
    actions = [("step", 0.001), ("tool", 0.001), ("step", 0.001)]
    out = run_with_breaker(actions, max_tool_calls=8, max_steps=12, max_usd=1.0)
    assert out["halted"] is False
    assert out["completed"] == 3
    assert out["trip_reason"] is None


def test_circuit_open_blocks_further():
    b = CircuitBreaker(max_tool_calls=1, max_steps=10, max_usd=10.0)
    b.note_tool_call(usd_delta=0.0)
    with pytest.raises(RuntimeError, match="max_tool_calls"):
        b.note_tool_call(usd_delta=0.0)
    with pytest.raises(RuntimeError, match="circuit open"):
        b.note_step()


def test_retry_storm_window():
    # 6 retries within 10s window, threshold 5
    events = [{"t": float(i), "kind": "retry", "provider": "openai"} for i in range(6)]
    out = detect_retry_storm(
        events, window_s=10.0, max_retries_in_window=5, max_consecutive_failures=99
    )
    assert out["flagged"] is True
    assert "retries_in_window" in out["reasons"]
    assert out["peak_retries_in_window"] == 6
    assert out["by_provider"]["openai"] == 6


def test_retry_storm_consecutive():
    events = [
        {"t": 0.0, "kind": "failure", "status": 500},
        {"t": 1.0, "kind": "retry", "status": 429},
        {"t": 2.0, "kind": "failure", "status": 503},
        {"t": 3.0, "kind": "success"},
    ]
    out = detect_retry_storm(
        events, window_s=60.0, max_retries_in_window=50, max_consecutive_failures=3
    )
    assert out["flagged"] is True
    assert "consecutive_failures" in out["reasons"]
    assert out["max_consecutive_failures"] == 3
    assert out["consecutive_trip_index"] == 2


def test_retry_storm_clean():
    events = [
        {"t": 0.0, "kind": "retry"},
        {"t": 1.0, "kind": "success"},
        {"t": 100.0, "kind": "retry"},
    ]
    out = detect_retry_storm(
        events, window_s=10.0, max_retries_in_window=2, max_consecutive_failures=3
    )
    assert out["flagged"] is False
    assert out["reasons"] == []


def test_retry_storm_bad_input():
    with pytest.raises(TypeError):
        detect_retry_storm("nope")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        detect_retry_storm([{"kind": "retry"}])  # missing t
