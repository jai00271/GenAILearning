"""Convergent checks for PROD 402 — decision helper + toy LoRA math."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from decide import compare_demo_vs_golden, recommend_adaptation  # noqa: E402
from lora_toy import (  # noqa: E402
    apply_lora,
    finetune_metric_comparison,
    lora_delta,
    lora_param_count,
    toy_preference_update,
)


def test_recommend_prompting_when_best():
    out = recommend_adaptation(
        {
            "prompting_score": 0.80,
            "rag_score": 0.70,
            "ft_score": 0.75,
            "data_available": True,
        }
    )
    assert out["recommendation"] == "prompting"
    assert out["demo_better_golden_worse"] is False


def test_recommend_rag_on_refresh():
    out = recommend_adaptation(
        {
            "prompting_score": 0.72,
            "rag_score": 0.71,
            "ft_score": 0.90,
            "data_available": True,
            "knowledge_needs_refresh": True,
            "catastrophic_forgetting_delta": 0.0,
        }
    )
    # FT ineligible under refresh; RAG preferred when within 0.05 of prompting
    assert out["eligible"]["finetune"] is False
    assert out["recommendation"] == "rag"
    assert "knowledge_needs_refresh" in out["flags"]


def test_recommend_finetune_when_clear_winner():
    out = recommend_adaptation(
        {
            "prompting_score": 0.60,
            "rag_score": 0.62,
            "ft_score": 0.85,
            "data_available": True,
            "eval_leakage_risk": False,
            "catastrophic_forgetting_delta": 0.01,
            "demo_score": 0.84,
            "golden_score": 0.83,
        }
    )
    assert out["recommendation"] == "finetune"


def test_refuse_finetune_on_leakage():
    out = recommend_adaptation(
        {
            "prompting_score": 0.50,
            "rag_score": 0.55,
            "ft_score": 0.99,
            "data_available": True,
            "eval_leakage_risk": True,
        }
    )
    assert out["recommendation"] in {"prompting", "rag"}
    assert out["eligible"]["finetune"] is False
    assert "eval_leakage_risk" in out["flags"]


def test_refuse_finetune_on_forgetting():
    out = recommend_adaptation(
        {
            "prompting_score": 0.50,
            "rag_score": 0.50,
            "ft_score": 0.95,
            "data_available": True,
            "catastrophic_forgetting_delta": 0.20,
        }
    )
    assert out["eligible"]["finetune"] is False
    assert out["recommendation"] in {"prompting", "rag"}


def test_demo_better_golden_worse_blocks_ft():
    out = recommend_adaptation(
        {
            "prompting_score": 0.40,
            "rag_score": 0.45,
            "ft_score": 0.99,
            "data_available": True,
            "demo_score": 0.95,
            "golden_score": 0.50,
            "catastrophic_forgetting_delta": 0.0,
        }
    )
    assert out["demo_better_golden_worse"] is True
    assert out["eligible"]["finetune"] is False
    assert out["recommendation"] in {"prompting", "rag"}


def test_compare_demo_vs_golden():
    hit = compare_demo_vs_golden(0.9, 0.7, gap=0.15)
    assert hit["demo_better_golden_worse"] is True
    miss = compare_demo_vs_golden(0.8, 0.75, gap=0.15)
    assert miss["demo_better_golden_worse"] is False


def test_lora_delta_and_apply():
    # out=2, in=3, r=1
    A = np.array([[1.0, 0.0, -1.0]])  # (1, 3)
    B = np.array([[2.0], [0.5]])  # (2, 1)
    delta = lora_delta(A, B, scale=1.0)
    assert delta.shape == (2, 3)
    np.testing.assert_allclose(delta, np.array([[2.0, 0.0, -2.0], [0.5, 0.0, -0.5]]))

    W = np.zeros((2, 3))
    W2 = apply_lora(W, A, B, scale=0.5)
    np.testing.assert_allclose(W2, 0.5 * delta)


def test_lora_shape_errors():
    with pytest.raises(ValueError):
        lora_delta([[1.0, 2.0]], [[1.0, 2.0]])  # B 1x2, A 1x2 — rank mismatch
    with pytest.raises(ValueError):
        apply_lora(np.zeros((3, 3)), [[1.0, 0.0]], [[1.0], [0.0]])  # delta 2x2


def test_lora_param_count():
    stats = lora_param_count(4096, 4096, rank=8)
    assert stats["full_ft_params"] == 4096 * 4096
    assert stats["lora_params"] == 8 * 4096 + 4096 * 8
    assert stats["saved_params"] == stats["full_ft_params"] - stats["lora_params"]
    assert stats["lora_params"] < stats["full_ft_params"]


def test_toy_preference_update():
    updated = toy_preference_update([0.5, 0.4, 0.6], preferred_idx=1, step=0.2)
    assert updated[1] == pytest.approx(0.6)
    assert updated[0] == pytest.approx(0.5 - 0.05)
    assert updated[2] == pytest.approx(0.6 - 0.05)


def test_finetune_metric_comparison_forgetting():
    before = {"demo": 0.70, "golden": 0.80, "preference_margin": 0.10}
    after = {"demo": 0.92, "golden": 0.60, "preference_margin": 0.25}
    out = finetune_metric_comparison(before, after)
    assert out["forgetting"] is True
    assert out["demo_better_golden_worse"] is True
    assert out["demo_delta"] == pytest.approx(0.22)
    assert out["golden_delta"] == pytest.approx(-0.20)
    assert out["preference_margin_delta"] == pytest.approx(0.15)


def test_finetune_metric_comparison_requires_keys():
    with pytest.raises(KeyError):
        finetune_metric_comparison({"demo": 1.0}, {"demo": 1.0, "golden": 1.0})
