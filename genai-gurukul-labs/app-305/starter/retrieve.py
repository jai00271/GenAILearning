"""APP 305 — retrieval + hybrid search + APP 304 metric wiring (starter)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Hashable, Iterable, Sequence

import numpy as np

from chunk import Chunk

LABS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "core-204"))
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "app-304"))

from embedder import Embedder, LocalEmbedder  # noqa: E402
from metrics import f1_at_k, precision_at_k, recall_at_k  # noqa: F401, E402


def embed_chunks(
    chunks: Sequence[Chunk],
    embedder: Embedder | None = None,
) -> np.ndarray:
    """Return (n_chunks, dim) embeddings."""
    # TODO: embed chunk texts via LocalEmbedder (or provided embedder)
    raise NotImplementedError


def semantic_search(
    query: str,
    chunks: Sequence[Chunk],
    vectors: np.ndarray,
    embedder: Embedder | None = None,
    k: int = 5,
) -> list[str]:
    """Rank by cosine; return chunk_ids."""
    # TODO: cosine rank using checkpoint embedder helpers
    raise NotImplementedError


def keyword_search(
    query: str,
    chunks: Sequence[Chunk],
    k: int = 5,
) -> list[str]:
    """Token-overlap score; down-weight quarantined OCR chunks."""
    # TODO: implement keyword overlap ranking
    raise NotImplementedError


def hybrid_search(
    query: str,
    chunks: Sequence[Chunk],
    vectors: np.ndarray,
    embedder: Embedder | None = None,
    k: int = 5,
    *,
    candidate_k: int | None = None,
) -> list[str]:
    """RRF fuse semantic + keyword rankings → chunk_ids."""
    # TODO: reciprocal rank fusion of semantic_search + keyword_search
    raise NotImplementedError


def chunk_ids_to_doc_ids(
    chunk_ids: Sequence[str],
    chunks: Sequence[Chunk],
) -> list[str]:
    """Map ranked chunk ids → unique doc ids (order-preserving)."""
    # TODO: dedupe by doc_id
    raise NotImplementedError


def retrieve_doc_ids(
    query: str,
    chunks: Sequence[Chunk],
    vectors: np.ndarray,
    *,
    mode: str = "hybrid",
    embedder: Embedder | None = None,
    k: int = 5,
) -> list[str]:
    """End-to-end retrieve returning ranked unique doc ids."""
    # TODO: dispatch on mode then map to doc ids
    raise NotImplementedError


def mean_precision_recall_at_k(
    ranked_doc_lists: Sequence[Sequence[Hashable]],
    relevant_sets: Sequence[Iterable[Hashable]],
    k: int,
) -> dict[str, float]:
    """Macro-average P@k / R@k / F1@k using APP 304 checkpoint metrics."""
    # TODO: call precision_at_k / recall_at_k / f1_at_k and average
    raise NotImplementedError
