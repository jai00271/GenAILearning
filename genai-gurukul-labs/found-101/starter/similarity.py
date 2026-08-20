"""FOUND-101 — cosine similarity helpers (starter)."""

from __future__ import annotations

import numpy as np


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    a = np.asanyarray(a, dtype=np.float64);
    b = np.asanyarray(b, dtype=np.float64);
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def most_similar(
    query: np.ndarray | list[float],
    corpus: np.ndarray | list[list[float]],
) -> int:
    """Return the index of the corpus row most similar to query (cosine)."""
    query = np.asanyarray(query, dtype=np.float64)
    corpus = np.asanyarray(corpus, dtype=np.float64)
    similarities = np.dot(corpus, query) / (np.linalg.norm(corpus, axis=1) * np.linalg.norm(query))
    return int(np.argmax(similarities))
    

if __name__ == "__main__":
    import numpy as np

    a = np.array([1.0, 0.0])
    b = np.array([1.0, 0.0])
    print(cosine_similarity(a, b))