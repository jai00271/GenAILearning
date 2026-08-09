"""FOUND-103 — TinyMLP 2→2→1 (solution)."""

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

    def hidden(self, x: np.ndarray | list[float]) -> np.ndarray:
        x_arr = np.asarray(x, dtype=float).ravel()
        z = x_arr @ self.W1 + self.b1
        return relu(z)

    def forward(self, x: np.ndarray | list[float]) -> float:
        h = self.hidden(x)
        return float(h @ self.W2 + self.b2)


def numerical_dL_dW2(
    model: TinyMLP,
    x: np.ndarray | list[float],
    y: float,
    eps: float = 1e-5,
) -> np.ndarray:
    """Finite-difference estimate of ∂L/∂W2 for L = (ŷ - y)^2."""
    grads = np.zeros_like(model.W2)
    for i in range(model.W2.size):
        original = model.W2[i]
        model.W2[i] = original + eps
        loss_plus = (model.forward(x) - y) ** 2
        model.W2[i] = original - eps
        loss_minus = (model.forward(x) - y) ** 2
        model.W2[i] = original
        grads[i] = (loss_plus - loss_minus) / (2.0 * eps)
    return grads


def train_step(model: TinyMLP, x: np.ndarray | list[float], y: float, lr: float = 0.1) -> float:
    """One SGD step using analytic grads for L = (ŷ - y)^2.

    Updates all parameters. Returns the pre-update loss.
    """
    x_arr = np.asarray(x, dtype=float).ravel()
    z = x_arr @ model.W1 + model.b1
    h = relu(z)
    y_hat = float(h @ model.W2 + model.b2)
    loss = (y_hat - y) ** 2

    dL_dy = 2.0 * (y_hat - y)
    dL_dW2 = dL_dy * h
    dL_db2 = dL_dy

    # Through ReLU: mask inactive units
    dL_dh = dL_dy * model.W2
    relu_mask = (z > 0).astype(float)
    dL_dz = dL_dh * relu_mask
    dL_dW1 = np.outer(x_arr, dL_dz)
    dL_db1 = dL_dz

    model.W2 = model.W2 - lr * dL_dW2
    model.b2 = model.b2 - lr * dL_db2
    model.W1 = model.W1 - lr * dL_dW1
    model.b1 = model.b1 - lr * dL_db1
    return float(loss)


def train_loop(
    model: TinyMLP,
    x: np.ndarray | list[float],
    y: float,
    steps: int = 50,
    lr: float = 0.1,
) -> list[float]:
    """Run train_step repeatedly; return loss history."""
    history: list[float] = []
    for _ in range(steps):
        history.append(train_step(model, x, y, lr=lr))
    return history
