"""FOUND-102 — vector geometry (solution)."""

from __future__ import annotations

import numpy as np


def dot(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    return float(np.dot(a, b))


def l2_norm(a: np.ndarray | list[float]) -> float:
    a = np.asarray(a, dtype=float).ravel()
    return float(np.linalg.norm(a))


def cosine(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Cosine similarity; 0.0 if either norm is 0."""
    na = l2_norm(a)
    nb = l2_norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot(a, b) / (na * nb)
