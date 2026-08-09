"""Convergent checks for CORE 202."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from attention import (  # noqa: E402
    causal_mask,
    combine_heads,
    multi_head_attention,
    scaled_dot_product_attention,
    softmax,
    split_heads,
)


def test_softmax_rows_sum_to_one():
    x = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
    p = softmax(x, axis=-1)
    assert p.shape == x.shape
    assert np.allclose(p.sum(axis=-1), 1.0)
    assert np.allclose(p[1], np.array([1 / 3, 1 / 3, 1 / 3]))


def test_causal_mask_blocks_future():
    m = causal_mask(3)
    assert m.shape == (3, 3)
    assert m[0, 0] == 0 and m[1, 1] == 0 and m[2, 2] == 0
    assert m[0, 1] <= -1e8 and m[0, 2] <= -1e8 and m[1, 2] <= -1e8
    assert m[1, 0] == 0 and m[2, 0] == 0 and m[2, 1] == 0


def test_scaled_dot_product_identity_like():
    # When Q=K=V = I-ish orthonormal rows, attention should prefer matching positions.
    Q = np.eye(3)
    K = np.eye(3)
    V = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])
    out, weights = scaled_dot_product_attention(Q, K, V)
    assert out.shape == (3, 2)
    assert weights.shape == (3, 3)
    assert np.allclose(weights.sum(axis=-1), 1.0)
    # Diagonal should dominate
    assert weights[0, 0] > weights[0, 1]
    assert weights[1, 1] > weights[1, 0]


def test_scaled_dot_product_with_causal_mask():
    rng = np.random.default_rng(0)
    Q = rng.normal(size=(4, 8))
    K = rng.normal(size=(4, 8))
    V = rng.normal(size=(4, 8))
    mask = causal_mask(4)
    _, weights = scaled_dot_product_attention(Q, K, V, mask=mask)
    # Strict upper triangle ≈ 0
    assert np.allclose(np.triu(weights, k=1), 0.0, atol=1e-7)


def test_split_combine_heads_roundtrip():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(5, 16))
    h = split_heads(x, num_heads=4)
    assert h.shape == (4, 5, 4)
    assert np.allclose(combine_heads(h), x)


def test_multi_head_shapes_and_causal():
    rng = np.random.default_rng(2)
    n, d = 6, 16
    X = rng.normal(size=(n, d))
    W_Q = rng.normal(size=(d, d))
    W_K = rng.normal(size=(d, d))
    W_V = rng.normal(size=(d, d))
    W_O = rng.normal(size=(d, d))
    out = multi_head_attention(X, W_Q, W_K, W_V, W_O, num_heads=4, causal=True)
    assert out.shape == (n, d)
    # Deterministic: same inputs → same outputs
    out2 = multi_head_attention(X, W_Q, W_K, W_V, W_O, num_heads=4, causal=True)
    assert np.allclose(out, out2)
