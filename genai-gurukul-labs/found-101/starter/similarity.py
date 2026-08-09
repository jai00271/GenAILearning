"""FOUND-101 — cosine similarity helpers (starter)."""

from __future__ import annotations

import numpy as np


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Return cosine similarity between vectors a and b.

    Return 0.0 if either vector has zero L2 norm.
    """
    raise NotImplementedError("Implement cosine_similarity in the starter lab")


def most_similar(
    query: np.ndarray | list[float],
    corpus: np.ndarray | list[list[float]],
) -> int:
    """Return the index of the corpus row most similar to query (cosine)."""
    raise NotImplementedError("Implement most_similar in the starter lab")
