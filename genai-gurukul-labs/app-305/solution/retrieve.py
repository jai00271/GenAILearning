"""APP 305 — retrieval + hybrid search + APP 304 metric wiring (solution).

Uses checkpoints/core-204 LocalEmbedder (or any Embedder) and
checkpoints/app-304 precision/recall@k helpers.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Hashable, Iterable, Sequence

import numpy as np

from chunk import Chunk

LABS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "core-204"))
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "app-304"))

from embedder import Embedder, LocalEmbedder, cosine_similarity  # noqa: E402
from metrics import f1_at_k, precision_at_k, recall_at_k  # noqa: E402

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def embed_chunks(
    chunks: Sequence[Chunk],
    embedder: Embedder | None = None,
) -> np.ndarray:
    """Return (n_chunks, dim) embeddings. Empty → shape (0, dim)."""
    emb = embedder or LocalEmbedder()
    if not chunks:
        return np.zeros((0, emb.dimensions), dtype=np.float64)
    return emb.embed([c.text for c in chunks])


def semantic_search(
    query: str,
    chunks: Sequence[Chunk],
    vectors: np.ndarray,
    embedder: Embedder | None = None,
    k: int = 5,
) -> list[str]:
    """Rank by cosine; return chunk_ids (length min(k, n))."""
    if k <= 0:
        raise ValueError("k must be positive")
    if not chunks:
        return []
    emb = embedder or LocalEmbedder()
    q = emb.embed([query])[0]
    scored = [
        (i, cosine_similarity(q, vectors[i]))
        for i in range(len(chunks))
    ]
    scored.sort(key=lambda x: (-x[1], x[0]))
    return [chunks[i].chunk_id for i, _ in scored[:k]]


def keyword_search(
    query: str,
    chunks: Sequence[Chunk],
    k: int = 5,
) -> list[str]:
    """Simple token-overlap score (teaching BM25-lite stand-in).

    score = |q ∩ d| / sqrt(|d|+1) — prefers denser overlap without real IDF.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    q_set = set(_tokens(query))
    if not chunks or not q_set:
        return []
    scored: list[tuple[int, float]] = []
    for i, ch in enumerate(chunks):
        # Down-weight quarantined OCR unless query explicitly asks about it
        toks = _tokens(ch.text)
        overlap = len(q_set & set(toks))
        score = overlap / (len(toks) ** 0.5 + 1.0)
        if ch.metadata.get("quarantine") and "ocr" not in query.lower():
            score *= 0.15
        scored.append((i, score))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return [chunks[i].chunk_id for i, s in scored[:k] if s > 0]


def _rrf_fuse(
    rankings: Sequence[Sequence[str]],
    k: int,
    rrf_k: int = 60,
) -> list[str]:
    """Reciprocal Rank Fusion over multiple ranked id lists."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / float(rrf_k + rank)
    ordered = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [cid for cid, _ in ordered[:k]]


def hybrid_search(
    query: str,
    chunks: Sequence[Chunk],
    vectors: np.ndarray,
    embedder: Embedder | None = None,
    k: int = 5,
    *,
    candidate_k: int | None = None,
) -> list[str]:
    """Hybrid = RRF(semantic, keyword). Returns chunk_ids."""
    if k <= 0:
        raise ValueError("k must be positive")
    ck = candidate_k or max(k * 3, k)
    sem = semantic_search(query, chunks, vectors, embedder=embedder, k=ck)
    kw = keyword_search(query, chunks, k=ck)
    return _rrf_fuse([sem, kw], k=k)


def chunk_ids_to_doc_ids(
    chunk_ids: Sequence[str],
    chunks: Sequence[Chunk],
) -> list[str]:
    """Map ranked chunk ids → doc ids, preserving order, deduping docs."""
    by_id = {c.chunk_id: c for c in chunks}
    out: list[str] = []
    seen: set[str] = set()
    for cid in chunk_ids:
        ch = by_id.get(cid)
        if ch is None:
            continue
        if ch.doc_id in seen:
            continue
        seen.add(ch.doc_id)
        out.append(ch.doc_id)
    return out


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
    if mode == "semantic":
        cids = semantic_search(query, chunks, vectors, embedder=embedder, k=max(k * 3, k))
    elif mode == "keyword":
        cids = keyword_search(query, chunks, k=max(k * 3, k))
    elif mode == "hybrid":
        cids = hybrid_search(query, chunks, vectors, embedder=embedder, k=max(k * 3, k))
    else:
        raise ValueError("mode must be semantic|keyword|hybrid")
    return chunk_ids_to_doc_ids(cids, chunks)[:k]


def mean_precision_recall_at_k(
    ranked_doc_lists: Sequence[Sequence[Hashable]],
    relevant_sets: Sequence[Iterable[Hashable]],
    k: int,
) -> dict[str, float]:
    """Macro-average P@k / R@k / F1@k using APP 304 checkpoint metrics."""
    if len(ranked_doc_lists) != len(relevant_sets):
        raise ValueError("ranked_doc_lists and relevant_sets length mismatch")
    if not ranked_doc_lists:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n": 0.0}
    ps, rs, fs = [], [], []
    for ranked, rel in zip(ranked_doc_lists, relevant_sets, strict=True):
        ps.append(precision_at_k(ranked, rel, k))
        rs.append(recall_at_k(ranked, rel, k))
        fs.append(f1_at_k(ranked, rel, k))
    return {
        "precision": float(np.mean(ps)),
        "recall": float(np.mean(rs)),
        "f1": float(np.mean(fs)),
        "n": float(len(ps)),
    }
