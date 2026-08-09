"""CORE 202 — scaled dot-product + multi-head attention (starter)."""

from __future__ import annotations

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax along axis."""
    # TODO: subtract max, exp, normalize
    raise NotImplementedError


def causal_mask(n: int) -> np.ndarray:
    """Return (n, n) mask of 0 on allowed positions and -1e9 on future positions.

    Allowed = j <= i (lower triangle including diagonal).
    """
    # TODO
    raise NotImplementedError


def scaled_dot_product_attention(
    Q: np.ndarray,
    K: np.ndarray,
    V: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute Attention(Q,K,V) = softmax((QKᵀ)/√dₖ + mask) V.

    Q: (n, d_k), K: (n, d_k), V: (n, d_v)
    mask: optional (n, n) added to scores before softmax
    Returns (output (n, d_v), weights (n, n)).
    """
    # TODO
    raise NotImplementedError


def split_heads(x: np.ndarray, num_heads: int) -> np.ndarray:
    """(n, d_model) → (num_heads, n, d_head) with d_model = num_heads * d_head."""
    # TODO
    raise NotImplementedError


def combine_heads(x: np.ndarray) -> np.ndarray:
    """(num_heads, n, d_head) → (n, d_model)."""
    # TODO
    raise NotImplementedError


def multi_head_attention(
    X: np.ndarray,
    W_Q: np.ndarray,
    W_K: np.ndarray,
    W_V: np.ndarray,
    W_O: np.ndarray,
    num_heads: int,
    causal: bool = False,
) -> np.ndarray:
    """Tiny MHA: project X, split heads, attend per head, concat, W_O.

    X: (n, d_model)
    W_Q,W_K,W_V: (d_model, d_model)
    W_O: (d_model, d_model)
    """
    # TODO
    raise NotImplementedError
