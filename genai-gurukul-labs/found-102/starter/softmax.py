"""FOUND-102 — softmax + temperature (starter)."""

from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray | list[float], temperature: float = 1.0) -> np.ndarray:
    """Numerically stable softmax with temperature T: softmax(z / T).

    temperature must be > 0.
    """
    raise NotImplementedError
