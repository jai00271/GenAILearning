"""CORE 202 — scaled dot-product + multi-head attention (solution)."""

from __future__ import annotations

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    shifted = x - np.max(x, axis=axis, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=axis, keepdims=True)


def causal_mask(n: int) -> np.ndarray:
    mask = np.zeros((n, n), dtype=np.float64)
    # j > i → future → block
    future = np.triu(np.ones((n, n), dtype=bool), k=1)
    mask[future] = -1e9
    return mask


def scaled_dot_product_attention(
    Q: np.ndarray,
    K: np.ndarray,
    V: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    Q = np.asarray(Q, dtype=np.float64)
    K = np.asarray(K, dtype=np.float64)
    V = np.asarray(V, dtype=np.float64)
    d_k = Q.shape[-1]
    scores = (Q @ K.T) / np.sqrt(d_k)
    if mask is not None:
        scores = scores + mask
    weights = softmax(scores, axis=-1)
    return weights @ V, weights


def split_heads(x: np.ndarray, num_heads: int) -> np.ndarray:
    n, d_model = x.shape
    if d_model % num_heads != 0:
        raise ValueError("d_model must be divisible by num_heads")
    d_head = d_model // num_heads
    # (n, h, d_head) → (h, n, d_head)
    return x.reshape(n, num_heads, d_head).transpose(1, 0, 2)


def combine_heads(x: np.ndarray) -> np.ndarray:
    h, n, d_head = x.shape
    return x.transpose(1, 0, 2).reshape(n, h * d_head)


def multi_head_attention(
    X: np.ndarray,
    W_Q: np.ndarray,
    W_K: np.ndarray,
    W_V: np.ndarray,
    W_O: np.ndarray,
    num_heads: int,
    causal: bool = False,
) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    Q = X @ W_Q
    K = X @ W_K
    V = X @ W_V
    Qh = split_heads(Q, num_heads)
    Kh = split_heads(K, num_heads)
    Vh = split_heads(V, num_heads)
    n = X.shape[0]
    mask = causal_mask(n) if causal else None
    heads = []
    for i in range(num_heads):
        out_i, _ = scaled_dot_product_attention(Qh[i], Kh[i], Vh[i], mask=mask)
        heads.append(out_i)
    stacked = np.stack(heads, axis=0)
    concat = combine_heads(stacked)
    return concat @ W_O
