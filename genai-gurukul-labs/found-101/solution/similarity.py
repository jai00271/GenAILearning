"""FOUND-101 — cosine similarity helpers (solution)."""

from __future__ import annotations

import numpy as np


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Return cosine similarity between vectors a and b.

    Return 0.0 if either vector has zero L2 norm.
    """
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def most_similar(
    query: np.ndarray | list[float],
    corpus: np.ndarray | list[list[float]],
) -> int:
    """Return the index of the corpus row most similar to query (cosine)."""
    corpus_arr = np.asarray(corpus, dtype=float)
    if corpus_arr.ndim != 2:
        raise ValueError("corpus must be 2-D")
    scores = [cosine_similarity(query, row) for row in corpus_arr]
    return int(np.argmax(scores))
