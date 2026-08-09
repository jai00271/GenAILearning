"""Convergent checks for APP 306 — vector index, tenant isolation, eval beat."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from vector_index import (  # noqa: E402
    NumpyVectorIndex,
    build_multitenant_fixture,
    cosine_similarity,
    l2_normalize,
    measure_latency_recall,
    metadata_matches,
    recall_at_k,
    tenant_isolation_bug_demo,
)


def test_l2_normalize_unit_and_zero():
    v = l2_normalize([3.0, 4.0])
    assert abs(float(np.linalg.norm(v)) - 1.0) < 1e-9
    z = l2_normalize([0.0, 0.0, 0.0])
    assert float(np.linalg.norm(z)) == 0.0


def test_cosine_similarity_known_and_zero():
    assert abs(cosine_similarity([1.0, 0.0], [1.0, 0.0]) - 1.0) < 1e-9
    assert abs(cosine_similarity([1.0, 0.0], [0.0, 1.0])) < 1e-9
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_metadata_matches_and_semantics():
    meta = {"tenant_id": "acme", "lang": "en"}
    assert metadata_matches(meta, None) is True
    assert metadata_matches(meta, {}) is True
    assert metadata_matches(meta, {"tenant_id": "acme"}) is True
    assert metadata_matches(meta, {"tenant_id": "acme", "lang": "en"}) is True
    assert metadata_matches(meta, {"tenant_id": "beta"}) is False
    assert metadata_matches(meta, {"tenant_id": "acme", "lang": "hi"}) is False


def test_recall_at_k():
    assert recall_at_k(["a1", "x", "a2"], {"a1", "a2"}, 3) == 1.0
    assert recall_at_k(["a1", "x", "a2"], {"a1", "a2"}, 1) == 0.5
    assert recall_at_k([], {"a1"}, 3) == 0.0
    assert recall_at_k(["a1"], set(), 1) == 0.0
    with pytest.raises(ValueError):
        recall_at_k(["a1"], {"a1"}, 0)


def test_index_add_search_basic():
    idx = NumpyVectorIndex(dimensions=2)
    idx.add(
        ids=["p", "q"],
        vectors=[[1.0, 0.0], [0.0, 1.0]],
        metadatas=[{"tenant_id": "acme"}, {"tenant_id": "beta"}],
    )
    assert len(idx) == 2
    hits = idx.search([1.0, 0.0], k=1)
    assert hits[0].id == "p"
    assert hits[0].score > 0.9


def test_index_rejects_duplicate_and_bad_dims():
    idx = NumpyVectorIndex(dimensions=2)
    idx.add(ids=["a"], vectors=[[1.0, 0.0]])
    with pytest.raises(ValueError):
        idx.add(ids=["a"], vectors=[[0.0, 1.0]])
    with pytest.raises(ValueError):
        idx.add(ids=["b"], vectors=[[1.0, 0.0, 0.0]])
    with pytest.raises(ValueError):
        NumpyVectorIndex(0)


def test_metadata_filter_excludes_other_tenant():
    idx = NumpyVectorIndex(dimensions=2)
    idx.add(
        ids=["a", "b"],
        vectors=[[1.0, 0.0], [0.99, 0.01]],
        metadatas=[{"tenant_id": "acme"}, {"tenant_id": "beta"}],
    )
    hits = idx.search([1.0, 0.0], k=2, filters={"tenant_id": "acme"})
    assert [h.id for h in hits] == ["a"]
    assert all(h.metadata["tenant_id"] == "acme" for h in hits)


def test_probe_fraction_limits_candidates():
    idx = NumpyVectorIndex(dimensions=2)
    # First two are orthogonal to query; gold is third.
    idx.add(
        ids=["noise1", "noise2", "gold"],
        vectors=[[0.0, 1.0], [0.0, 0.9], [1.0, 0.0]],
        metadatas=[{"tenant_id": "t"}, {"tenant_id": "t"}, {"tenant_id": "t"}],
    )
    miss = idx.search([1.0, 0.0], k=1, filters={"tenant_id": "t"}, probe_fraction=0.34)
    assert miss[0].id != "gold"
    hit = idx.search([1.0, 0.0], k=1, filters={"tenant_id": "t"}, probe_fraction=1.0)
    assert hit[0].id == "gold"


def test_tenant_isolation_bug_demo_on_fixture():
    index, queries = build_multitenant_fixture()
    assert len(index) >= 10
    q = queries[0].query_vector
    demo = tenant_isolation_bug_demo(index, q, tenant_id="acme", k=5)
    assert demo["shared_collection_safe_without_filter"] is False
    assert demo["leak_detected"] is True
    assert "b1" in demo["foreign_tenant_ids_unfiltered"]
    assert demo["foreign_tenant_ids_filtered"] == []
    assert "b1" not in demo["filtered_hit_ids"]
    filtered = index.search(q, k=5, filters={"tenant_id": "acme"})
    assert all(h.metadata.get("tenant_id") == "acme" for h in filtered)


def test_measure_latency_recall_tradeoff():
    index, queries = build_multitenant_fixture()
    rows = measure_latency_recall(
        index,
        queries,
        k=3,
        probe_fractions=(0.25, 1.0),
        repeats=3,
    )
    assert len(rows) == 2
    low, full = rows[0], rows[1]
    assert low["probe_fraction"] == 0.25
    assert full["probe_fraction"] == 1.0
    assert full["mean_recall_at_k"] > low["mean_recall_at_k"]
    assert full["mean_recall_at_k"] == pytest.approx(1.0)
    assert low["mean_latency_ms"] >= 0.0
    assert full["mean_latency_ms"] >= 0.0
    assert full["n_measurements"] == 3 * len(queries)
