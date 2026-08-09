"""Convergent checks for APP 304 — evaluation fundamentals."""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from golden import (  # noqa: E402
    find_leakage,
    golden_questions,
    load_golden_jsonl,
    normalize_text,
)
from metrics import (  # noqa: E402
    cohens_kappa,
    f1_at_k,
    mean_reciprocal_rank,
    mcnemar_contingency,
    paired_bootstrap_pvalue,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_normalize_text_collapses_noise():
    assert normalize_text("  How DO I reset an Okta password?! ") == "how do i reset an okta password"


def test_load_golden_jsonl_ok():
    rows = load_golden_jsonl(FIXTURES / "golden_ok.jsonl")
    assert len(rows) == 4
    assert rows[0]["id"] == "q1"
    assert rows[0]["relevant_ids"] == ["rb-okta-1", "rb-okta-2"]
    assert golden_questions(rows)[1].startswith("Why are auth")


def test_load_golden_jsonl_rejects_missing_keys(tmp_path: Path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"id": "x", "question": "hi"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="relevant_ids"):
        load_golden_jsonl(bad)


def test_find_leakage_detects_normalized_overlap():
    train = [
        "Reset VPN token steps",
        "How do I reset an Okta password?",
    ]
    eval_qs = [
        "how do i reset an okta password!",
        "unrelated billing question",
    ]
    hits = find_leakage(train, eval_qs)
    assert len(hits) == 1
    assert hits[0]["train_index"] == 1
    assert hits[0]["eval_index"] == 0


def test_find_leakage_no_hit():
    assert find_leakage(["alpha"], ["beta"]) == []


def test_precision_recall_f1_at_k():
    retrieved = ["a", "x", "b", "y"]
    relevant = frozenset({"a", "b", "c"})
    assert precision_at_k(retrieved, relevant, 2) == pytest.approx(0.5)
    assert recall_at_k(retrieved, relevant, 2) == pytest.approx(1.0 / 3.0)
    p, r = (0.5, 0.3333333333333333)
    assert f1_at_k(retrieved, relevant, 2) == pytest.approx(2.0 * p * r / (p + r))
    assert precision_at_k(retrieved, relevant, 4) == pytest.approx(0.5)
    assert recall_at_k(retrieved, relevant, 4) == pytest.approx(2.0 / 3.0)


def test_recall_empty_relevant_is_zero():
    assert recall_at_k(["a"], [], 1) == 0.0
    assert f1_at_k(["a"], [], 1) == 0.0


def test_precision_rejects_nonpositive_k():
    with pytest.raises(ValueError):
        precision_at_k(["a"], ["a"], 0)


def test_mrr_and_reciprocal_rank():
    ranked = [["x", "doc1"], ["a", "b"]]
    rels = [{"doc1"}, {"z"}]
    assert reciprocal_rank(ranked[0], rels[0]) == pytest.approx(0.5)
    assert reciprocal_rank(ranked[1], rels[1]) == 0.0
    assert mean_reciprocal_rank(ranked, rels) == pytest.approx(0.25)


def test_cohens_kappa_perfect_and_chance():
    assert cohens_kappa(["yes", "no", "yes"], ["yes", "no", "yes"]) == pytest.approx(1.0)
    assert cohens_kappa(["a", "a", "a"], ["a", "a", "a"]) == pytest.approx(1.0)

    a = [0, 0, 1, 1, 0, 1, 1, 0, 0, 1]
    b = [0, 1, 1, 1, 0, 0, 1, 0, 0, 1]
    n = len(a)
    p_o = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    p_e = sum((ca[lab] / n) * (cb[lab] / n) for lab in set(ca) | set(cb))
    expected = (p_o - p_e) / (1 - p_e)
    assert cohens_kappa(a, b) == pytest.approx(expected)


def test_mcnemar_71_to_74_style():
    # 68 both right, 23 both wrong, 3 A-only, 6 B-only → 71% vs 74%.
    y = [1] * 100
    pred_a = [1] * 68 + [0] * 23 + [1] * 3 + [0] * 6
    pred_b = [1] * 68 + [0] * 23 + [0] * 3 + [1] * 6
    assert sum(a == t for a, t in zip(pred_a, y)) == 71
    assert sum(b == t for b, t in zip(pred_b, y)) == 74
    out = mcnemar_contingency(y, pred_a, pred_b)
    assert out["b"] == 6
    assert out["c"] == 3
    assert out["n_discordant"] == 9
    assert out["statistic"] == pytest.approx((6 - 3) ** 2 / 9)
    assert 0.0 < out["p_value"] < 1.0


def test_paired_bootstrap_detects_clear_gain():
    rng = np.random.default_rng(0)
    scores_a = rng.random(80)
    scores_b = scores_a + 0.2
    out = paired_bootstrap_pvalue(scores_a, scores_b, n_bootstrap=2000, seed=1)
    assert out["observed_delta"] == pytest.approx(0.2)
    assert out["p_value"] < 0.05


def test_paired_bootstrap_nullish_delta_not_tiny_p():
    s = [0.0, 1.0, 1.0, 0.0, 1.0, 0.0] * 10
    out = paired_bootstrap_pvalue(
        s, s, n_bootstrap=1000, seed=2, alternative="greater"
    )
    assert out["observed_delta"] == pytest.approx(0.0)
    assert out["p_value"] >= 0.4
