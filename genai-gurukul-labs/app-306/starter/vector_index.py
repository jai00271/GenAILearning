"""APP 306 — in-memory vector index with metadata filters (starter).

Numpy stand-in for Chroma / FAISS / managed vector DBs. Exact cosine search,
AND metadata filters, tenant-isolation leak demo, and a probe-fraction
latency↔recall eval beat (ANN nprobe / efSearch teaching analogy).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest app-306/tests -q
(or compare against solution/).
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
    # TODO
    raise NotImplementedError


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Cosine; 0.0 if either vector has zero L2 norm (FOUND 101 / CORE 204)."""
    # TODO
    raise NotImplementedError


def metadata_matches(meta: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    """AND exact-match filters. ``None`` or empty filters → always True."""
    # TODO
    raise NotImplementedError


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str] | frozenset[str],
    k: int,
) -> float:
    """R@k = |retrieved[:k] ∩ relevant| / |relevant|; empty relevant → 0.0."""
    # TODO
    raise NotImplementedError


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
        # TODO: validate shapes; store copies; reject duplicate ids
        raise NotImplementedError

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
        # TODO
        raise NotImplementedError


def build_multitenant_fixture() -> tuple[NumpyVectorIndex, list[EvalQuery]]:
    """Small shared-collection fixture: two tenants, overlapping query geometry.

    Dim=4. Tenant ``acme`` owns fillers + a1/a2; ``beta`` owns beta fillers + b1/b2.
    Gold docs are appended *after* same-tenant fillers so ``probe_fraction`` < 1
    can drop recall (ANN nprobe teaching analogy). ``b1`` sits near the acme
    query axis so an unfiltered search can leak beta into an acme session.
    """
    # TODO: match solution fixture layout (see solution/vector_index.py)
    raise NotImplementedError


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
    # TODO: compare filters=None vs filters={"tenant_id": tenant_id}
    raise NotImplementedError


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
    # TODO: time search; aggregate mean_latency_ms + mean_recall_at_k per frac
    raise NotImplementedError
