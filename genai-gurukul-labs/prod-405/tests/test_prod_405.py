"""Convergent checks for PROD 405 — latency budgets, TPM planner, failover."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from failover_router import ProviderResult, route_with_failover  # noqa: E402
from latency_budget import check_latency_budgets  # noqa: E402
from tpm_planner import plan_tpm, plan_tpm_from_mix  # noqa: E402


def test_latency_both_pass():
    samples = [
        {"ttft_ms": 200, "total_ms": 1200},
        {"ttft_ms": 250, "total_ms": 1400},
        {"ttft_ms": 180, "total_ms": 1100},
        {"ttft_ms": 220, "total_ms": 1300},
    ]
    out = check_latency_budgets(
        samples, ttft_budget_ms=300, total_budget_ms=2000, p_threshold=0.75
    )
    assert out["passed"] is True
    assert out["failed_budgets"] == []
    assert out["ttft"]["passed"] is True
    assert out["total"]["passed"] is True


def test_latency_ttft_fails_total_ok():
    samples = [
        {"ttft_ms": 800, "total_ms": 1500},
        {"ttft_ms": 900, "total_ms": 1600},
        {"ttft_ms": 850, "total_ms": 1550},
        {"ttft_ms": 200, "total_ms": 1400},
    ]
    out = check_latency_budgets(
        samples, ttft_budget_ms=300, total_budget_ms=2000, p_threshold=0.75
    )
    assert out["passed"] is False
    assert "ttft" in out["failed_budgets"]
    assert "total" not in out["failed_budgets"]


def test_latency_total_fails():
    samples = [
        {"ttft_ms": 100, "total_ms": 5000},
        {"ttft_ms": 110, "total_ms": 5100},
        {"ttft_ms": 120, "total_ms": 5200},
        {"ttft_ms": 90, "total_ms": 900},
    ]
    out = check_latency_budgets(
        samples, ttft_budget_ms=300, total_budget_ms=2000, p_threshold=0.75
    )
    assert out["passed"] is False
    assert "total" in out["failed_budgets"]


def test_latency_rejects_total_lt_ttft():
    with pytest.raises(ValueError):
        check_latency_budgets(
            [{"ttft_ms": 500, "total_ms": 100}],
            ttft_budget_ms=300,
            total_budget_ms=2000,
        )


def test_plan_tpm_fits():
    out = plan_tpm(
        requests_per_minute=10,
        avg_tokens_in=500,
        avg_tokens_out=500,
        provider_tpm_limit=100_000,
        safety_factor=0.8,
    )
    assert out["demand_tpm"] == pytest.approx(10_000.0)
    assert out["fits"] is True
    assert out["shards_needed"] == 1
    assert out["recommendation"] == "ok_within_headroom"


def test_plan_tpm_over_budget():
    out = plan_tpm(
        requests_per_minute=100,
        avg_tokens_in=2000,
        avg_tokens_out=2000,
        provider_tpm_limit=50_000,
        safety_factor=0.8,
    )
    assert out["demand_tpm"] == pytest.approx(400_000.0)
    assert out["fits"] is False
    assert out["shards_needed"] >= 2
    assert "scale_out" in out["recommendation"]


def test_plan_tpm_mix():
    mix = plan_tpm_from_mix(
        {
            "openai": {
                "rpm": 10,
                "avg_tokens_in": 100,
                "avg_tokens_out": 100,
                "tpm_limit": 100_000,
            },
            "anthropic": {
                "rpm": 1000,
                "avg_tokens_in": 2000,
                "avg_tokens_out": 2000,
                "tpm_limit": 10_000,
            },
        }
    )
    assert mix["fits_all"] is False
    assert mix["by_provider"]["openai"]["fits"] is True
    assert mix["by_provider"]["anthropic"]["fits"] is False


def test_plan_tpm_validation():
    with pytest.raises(ValueError):
        plan_tpm(
            requests_per_minute=1,
            avg_tokens_in=1,
            avg_tokens_out=1,
            provider_tpm_limit=100,
            safety_factor=0.0,
        )


def test_failover_primary_ok():
    out = route_with_failover(
        ["a", "b"],
        [
            ProviderResult(provider="a", ok=True, text="hello", ttft_ms=100, total_ms=500),
            ProviderResult(provider="b", ok=True, text="other"),
        ],
        mid_stream_timeout_ms=5_000,
    )
    assert out["ok"] is True
    assert out["provider"] == "a"
    assert out["text"] == "hello"


def test_failover_on_error_then_success():
    out = route_with_failover(
        ["a", "b"],
        [
            ProviderResult(provider="a", ok=False, error="500"),
            ProviderResult(provider="b", ok=True, text="fallback", total_ms=400),
        ],
        failure_threshold=1,
    )
    assert out["ok"] is True
    assert out["provider"] == "b"
    assert "a" in out["open_providers"]


def test_failover_mid_stream_timeout():
    out = route_with_failover(
        ["slow", "fast"],
        [
            ProviderResult(
                provider="slow", ok=True, text="partial", ttft_ms=50, total_ms=9_000
            ),
            ProviderResult(
                provider="fast", ok=True, text="done", ttft_ms=80, total_ms=400
            ),
        ],
        mid_stream_timeout_ms=2_000,
        failure_threshold=1,
    )
    assert out["ok"] is True
    assert out["provider"] == "fast"
    reasons = [a.get("reason") for a in out["attempts"] if not a.get("ok")]
    assert "mid_stream_timeout" in reasons


def test_failover_all_fail():
    out = route_with_failover(
        ["a", "b"],
        [
            ProviderResult(provider="a", ok=False, error="down"),
            ProviderResult(provider="b", ok=False, error="down"),
        ],
        failure_threshold=1,
    )
    assert out["ok"] is False
    assert out["provider"] is None
