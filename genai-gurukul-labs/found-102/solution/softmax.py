"""FOUND-102 — softmax + temperature (solution)."""

from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray | list[float], temperature: float = 1.0) -> np.ndarray:
    """Numerically stable softmax with temperature T: softmax(z / T).

    temperature must be > 0.
    """
    if temperature <= 0:
        raise ValueError("temperature must be > 0")
    z = np.asarray(logits, dtype=float).ravel() / float(temperature)
    z = z - np.max(z)
    exp_z = np.exp(z)
    return exp_z / exp_z.sum()
