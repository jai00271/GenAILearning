"""FOUND-102 — vector geometry (starter)."""

from __future__ import annotations

import numpy as np


def dot(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Dot product of two vectors."""
    a = np.asanyarray(a, dtype=np.float64)
    b = np.asanyarray(b, dtype=np.float64)
    return float(np.dot(a, b))


def l2_norm(a: np.ndarray | list[float]) -> float:
    """L2 norm (Euclidean length) of a vector."""
    a = np.asanyarray(a, dtype=np.float64)
    return float(np.linalg.norm(a))


def cosine(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Cosine similarity; 0.0 if either norm is 0."""
    a = np.asanyarray(a, dtype=np.float64)
    b = np.asanyarray(b, dtype=np.float64)
    norm_a = l2_norm(a)
    norm_b = l2_norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot(a, b) / (norm_a * norm_b)
