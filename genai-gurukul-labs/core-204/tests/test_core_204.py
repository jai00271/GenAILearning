"""Convergent checks for CORE 204."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from embedder import (  # noqa: E402
    FixtureEmbedder,
    LocalEmbedder,
    cosine_similarity,
    negation_failure_demo,
    rank_documents,
)


def test_local_embedder_deterministic_and_shaped():
    emb = LocalEmbedder(dimensions=32)
    a = emb.embed(["VPN password reset runbook"])
    b = emb.embed(["VPN password reset runbook"])
    assert a.shape == (1, 32)
    assert np.allclose(a, b)
    # Unit-ish after L2 normalize (non-empty text)
    assert abs(float(np.linalg.norm(a[0])) - 1.0) < 1e-9


def test_local_embedder_empty_batch():
    emb = LocalEmbedder(dimensions=16)
    out = emb.embed([])
    assert out.shape == (0, 16)


def test_cosine_zero_safe_and_identical():
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_rank_documents_prefers_lexical_overlap():
    docs = [
        "How to reset your corporate VPN password from Okta",
        "Quarterly cafeteria menu and catering schedule",
        "Invoice dispute workflow for accounts payable",
    ]
    ranked = rank_documents("VPN password reset", docs, embedder=LocalEmbedder())
    assert len(ranked) == 3
    assert ranked[0][0] == 0
    # Scores descending
    scores = [s for _, s in ranked]
    assert scores == sorted(scores, reverse=True)


def test_fixture_embedder_ranking():
    table = {
        "q": [1.0, 0.0, 0.0],
        "doc_match": [0.9, 0.1, 0.0],
        "doc_other": [0.0, 1.0, 0.0],
    }
    emb = FixtureEmbedder(table)
    ranked = rank_documents("q", ["doc_other", "doc_match"], embedder=emb)
    assert ranked[0][0] == 1
    assert ranked[0][1] > ranked[1][1]


def test_negation_failure_demo_documents_failure_mode():
    """Honest assertion: naive ngram embedder ranks negation closer than unrelated topic."""
    result = negation_failure_demo(LocalEmbedder())
    assert set(result) == {"sim_affirmative_negated", "sim_affirmative_unrelated"}
    assert result["sim_affirmative_negated"] > result["sim_affirmative_unrelated"]
    # Strong lexical overlap → high similarity (failure for truth-sensitive retrieval)
    assert result["sim_affirmative_negated"] > 0.7
