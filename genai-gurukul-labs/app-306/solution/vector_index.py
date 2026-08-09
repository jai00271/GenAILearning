"""APP 306 — in-memory vector index with metadata filters (solution).

Numpy stand-in for Chroma / FAISS / managed vector DBs. Exact cosine search,
AND metadata filters, tenant-isolation leak demo, and a probe-fraction
latency↔recall eval beat (ANN nprobe / efSearch teaching analogy).

Offline only — no Pinecone, OpenSearch, or FAISS dependency.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ScoredDoc:
    """One retrieval hit: id, cosine score, metadata copy."""

    id: str
    score: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class EvalQuery:
    """Golden query for the latency↔recall fixture."""

    query_vector: np.ndarray
    relevant_ids: frozenset[str]
    tenant_id: str


def l2_normalize(vec: np.ndarray) -> np.ndarray:
    """Return a unit-L2 copy; zero vector stays zero."""
    v = np.asarray(vec, dtype=np.float64).ravel()
    norm = float(np.linalg.norm(v))
    if norm == 0.0:
        return v.copy()
    return v / norm


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Cosine; 0.0 if either vector has zero L2 norm (FOUND 101 / CORE 204)."""
    aa = np.asarray(a, dtype=np.float64).ravel()
    bb = np.asarray(b, dtype=np.float64).ravel()
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom == 0.0:
        return 0.0
    return float(np.dot(aa, bb) / denom)


def metadata_matches(meta: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    """AND exact-match filters. ``None`` or empty filters → always True."""
    if not filters:
        return True
    for key, expected in filters.items():
        if meta.get(key) != expected:
            return False
    return True


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str] | frozenset[str],
    k: int,
) -> float:
    """R@k = |retrieved[:k] ∩ relevant| / |relevant|; empty relevant → 0.0."""
    if k <= 0:
        raise ValueError("k must be positive")
    rel = set(relevant_ids)
    if not rel:
        return 0.0
    top = list(retrieved_ids)[:k]
    tp = sum(1 for d in top if d in rel)
    return tp / float(len(rel))


class NumpyVectorIndex:
    """Brute-force in-memory cosine index with optional metadata filters.

    Teaching stand-in for local Chroma/FAISS collections and for the filter
    surface of Pinecone / OpenSearch k-NN / pgvector. Shared collection +
    forgotten ``tenant_id`` filter is **not** multi-tenant-safe — see
    ``tenant_isolation_bug_demo``.
    """

    def __init__(self, dimensions: int) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be >= 1")
        self.dimensions = dimensions
        self._ids: list[str] = []
        self._vectors: list[np.ndarray] = []
        self._metadatas: list[dict[str, Any]] = []
        self._id_to_pos: dict[str, int] = {}

    def __len__(self) -> int:
        return len(self._ids)

    def add(
        self,
        *,
        ids: list[str],
        vectors: np.ndarray | list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Append vectors. Duplicate ids raise ValueError."""
        mat = np.asarray(vectors, dtype=np.float64)
        if mat.ndim == 1:
            mat = mat.reshape(1, -1)
        if mat.ndim != 2:
            raise ValueError("vectors must be 2-D (n, dimensions)")
        if mat.shape[0] != len(ids):
            raise ValueError("ids and vectors length mismatch")
        if mat.shape[1] != self.dimensions:
            raise ValueError(f"expected dimensions={self.dimensions}, got {mat.shape[1]}")
        if metadatas is None:
            metas = [{} for _ in ids]
        else:
            if len(metadatas) != len(ids):
                raise ValueError("metadatas and ids length mismatch")
            metas = [dict(m) for m in metadatas]

        for i, doc_id in enumerate(ids):
            if not doc_id:
                raise ValueError("id must be non-empty")
            if doc_id in self._id_to_pos:
                raise ValueError(f"duplicate id: {doc_id}")
            self._id_to_pos[doc_id] = len(self._ids)
            self._ids.append(doc_id)
            self._vectors.append(np.asarray(mat[i], dtype=np.float64).ravel().copy())
            self._metadatas.append(metas[i])

    def search(
        self,
        query: np.ndarray | list[float],
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None,
        probe_fraction: float = 1.0,
    ) -> list[ScoredDoc]:
        """Top-k by cosine after AND metadata filters.

        ``probe_fraction`` in (0, 1] keeps only the first ceil(n_cand * f)
        filtered candidates (insertion order) before scoring — deterministic
        stand-in for ANN nprobe / efSearch. f=1.0 = exact over the filter set.
        """
        if k <= 0:
            raise ValueError("k must be positive")
        if not (0.0 < probe_fraction <= 1.0):
            raise ValueError("probe_fraction must be in (0, 1]")

        q = np.asarray(query, dtype=np.float64).ravel()
        if q.shape[0] != self.dimensions:
            raise ValueError(f"query dim {q.shape[0]} != index dimensions {self.dimensions}")

        candidates = [
            i
            for i, meta in enumerate(self._metadatas)
            if metadata_matches(meta, filters)
        ]
        if not candidates:
            return []

        n_probe = max(1, int(np.ceil(len(candidates) * probe_fraction)))
        probed = candidates[:n_probe]

        scored: list[ScoredDoc] = []
        for i in probed:
            score = cosine_similarity(q, self._vectors[i])
            scored.append(
                ScoredDoc(
                    id=self._ids[i],
                    score=score,
                    metadata=dict(self._metadatas[i]),
                )
            )
        scored.sort(key=lambda h: (-h.score, h.id))
        return scored[:k]


def build_multitenant_fixture() -> tuple[NumpyVectorIndex, list[EvalQuery]]:
    """Small shared-collection fixture: two tenants, overlapping query geometry.

    Dim=4. Tenant ``acme`` owns fillers + a1/a2; ``beta`` owns beta fillers + b1/b2.
    Gold docs are appended *after* same-tenant fillers so ``probe_fraction`` < 1
    can drop recall (ANN nprobe teaching analogy). ``b1`` sits near the acme
    query axis so an unfiltered search can leak beta into an acme session.
    """
    index = NumpyVectorIndex(dimensions=4)
    acme_fillers = [l2_normalize([0.0, 1.0, float(i) * 0.02, 0.0]) for i in range(8)]
    a1 = l2_normalize([1.0, 0.05, 0.0, 0.0])
    a2 = l2_normalize([0.95, 0.2, 0.0, 0.0])
    beta_fillers = [l2_normalize([0.0, 0.0, 0.0, 1.0 + float(i) * 0.01]) for i in range(4)]
    # Leak bait: close to acme query axis but tagged beta
    b1 = l2_normalize([0.98, 0.1, 0.05, 0.0])
    b2 = l2_normalize([0.0, 0.0, 1.0, 0.0])

    index.add(
        ids=[f"af{i}" for i in range(8)] + ["a1", "a2"] + [f"bf{i}" for i in range(4)] + ["b1", "b2"],
        vectors=np.stack([*acme_fillers, a1, a2, *beta_fillers, b1, b2], axis=0),
        metadatas=(
            [{"tenant_id": "acme", "doc": f"filler-{i}"} for i in range(8)]
            + [
                {"tenant_id": "acme", "doc": "password-reset"},
                {"tenant_id": "acme", "doc": "okta-mfa"},
            ]
            + [{"tenant_id": "beta", "doc": f"filler-{i}"} for i in range(4)]
            + [
                {"tenant_id": "beta", "doc": "password-reset"},
                {"tenant_id": "beta", "doc": "billing-faq"},
            ]
        ),
    )

    q_acme = l2_normalize([1.0, 0.0, 0.0, 0.0])
    q_beta = l2_normalize([0.0, 0.0, 1.0, 0.0])
    queries = [
        EvalQuery(
            query_vector=q_acme,
            relevant_ids=frozenset({"a1", "a2"}),
            tenant_id="acme",
        ),
        EvalQuery(
            query_vector=q_beta,
            relevant_ids=frozenset({"b2"}),
            tenant_id="beta",
        ),
    ]
    return index, queries


def tenant_isolation_bug_demo(
    index: NumpyVectorIndex,
    query: np.ndarray | list[float],
    *,
    tenant_id: str,
    k: int = 5,
) -> dict[str, Any]:
    """Prove shared collection + omitted filter is not multi-tenant-safe.

    Returns hit id lists and foreign-tenant leaks for unfiltered vs filtered
    search. ``foreign_tenant_ids_filtered`` must be empty when the filter is
    applied correctly. Deepened in PROD 405; named here so RAG apps do not
    ship the bug.
    """
    unfiltered = index.search(query, k=k, filters=None)
    filtered = index.search(query, k=k, filters={"tenant_id": tenant_id})

    foreign_unfiltered = [
        h.id for h in unfiltered if h.metadata.get("tenant_id") != tenant_id
    ]
    foreign_filtered = [
        h.id for h in filtered if h.metadata.get("tenant_id") != tenant_id
    ]
    return {
        "tenant_id": tenant_id,
        "unfiltered_hit_ids": [h.id for h in unfiltered],
        "filtered_hit_ids": [h.id for h in filtered],
        "foreign_tenant_ids_unfiltered": foreign_unfiltered,
        "foreign_tenant_ids_filtered": foreign_filtered,
        "shared_collection_safe_without_filter": False,
        "leak_detected": len(foreign_unfiltered) > 0,
    }


def measure_latency_recall(
    index: NumpyVectorIndex,
    queries: list[EvalQuery],
    *,
    k: int = 3,
    probe_fractions: list[float] | tuple[float, ...] = (0.25, 0.5, 1.0),
    repeats: int = 5,
) -> list[dict[str, float | int]]:
    """Eval beat: mean latency_ms and mean recall@k vs probe_fraction.

    Each query is searched with its ``tenant_id`` filter (correct isolation).
    Lower probe_fraction ≈ cheaper ANN probe, usually lower recall on this
    fixture when gold docs sit late in the candidate list.
    """
    if repeats < 1:
        raise ValueError("repeats must be >= 1")
    if not queries:
        raise ValueError("queries must be non-empty")

    rows: list[dict[str, float | int]] = []
    for frac in probe_fractions:
        latencies: list[float] = []
        recalls: list[float] = []
        for _ in range(repeats):
            for eq in queries:
                t0 = time.perf_counter()
                hits = index.search(
                    eq.query_vector,
                    k=k,
                    filters={"tenant_id": eq.tenant_id},
                    probe_fraction=float(frac),
                )
                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000.0)
                recalls.append(recall_at_k([h.id for h in hits], set(eq.relevant_ids), k))
        rows.append(
            {
                "probe_fraction": float(frac),
                "k": int(k),
                "mean_latency_ms": float(sum(latencies) / len(latencies)),
                "mean_recall_at_k": float(sum(recalls) / len(recalls)),
                "n_measurements": len(latencies),
            }
        )
    return rows
