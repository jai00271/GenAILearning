"""FOUND-103 — TinyMLP 2→2→1 (starter)."""

from __future__ import annotations

import numpy as np


def relu(z: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, z)


class TinyMLP:
    """Minimal MLP: input 2 → hidden 2 (ReLU) → output 1 (linear)."""

    def __init__(
        self,
        W1: np.ndarray | None = None,
        b1: np.ndarray | None = None,
        W2: np.ndarray | None = None,
        b2: float | np.ndarray | None = None,
    ) -> None:
        # Default fixture yields ŷ = 0.17 for x = [1, 2]
        self.W1 = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=float) if W1 is None else np.asarray(W1, dtype=float)
        self.b1 = np.zeros(2, dtype=float) if b1 is None else np.asarray(b1, dtype=float)
        self.W2 = np.array([0.1, 0.1], dtype=float) if W2 is None else np.asarray(W2, dtype=float).ravel()
        if b2 is None:
            self.b2 = 0.0
        else:
            self.b2 = float(np.asarray(b2).reshape(()))

    def forward(self, x: np.ndarray | list[float]) -> float:
        """Return scalar prediction ŷ."""
        raise NotImplementedError

    def hidden(self, x: np.ndarray | list[float]) -> np.ndarray:
        """Return post-ReLU hidden activations (useful for grad checks)."""
        raise NotImplementedError


def numerical_dL_dW2(
    model: TinyMLP,
    x: np.ndarray | list[float],
    y: float,
    eps: float = 1e-5,
) -> np.ndarray:
    """Finite-difference estimate of ∂L/∂W2 for L = (ŷ - y)^2."""
    raise NotImplementedError


def train_step(model: TinyMLP, x: np.ndarray | list[float], y: float, lr: float = 0.1) -> float:
    """One SGD step on W2/b2 (and optionally W1/b1) using analytic grads for MSE.

    Returns the pre-update loss.
    """
    raise NotImplementedError


def train_loop(
    model: TinyMLP,
    x: np.ndarray | list[float],
    y: float,
    steps: int = 50,
    lr: float = 0.1,
) -> list[float]:
    """Run train_step repeatedly; return loss history."""
    raise NotImplementedError
