"""FOUND-102 — softmax + temperature (starter)."""

from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray | list[float], temperature: float = 1.0) -> np.ndarray:
    """Numerically stable softmax with temperature T: softmax(z / T).

    temperature must be > 0.
    """
    logits = np.asarray(logits)
    if temperature <= 0:
        raise ValueError("Temperature must be greater than 0.")
    # Scale logits by temperature
    scaled_logits = logits / temperature
    # Subtract max for numerical stability
    shifted_logits = scaled_logits - np.max(scaled_logits)
    exp_logits = np.exp(shifted_logits)
    return exp_logits / np.sum(exp_logits)
