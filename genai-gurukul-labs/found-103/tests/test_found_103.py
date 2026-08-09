"""Tests for FOUND-103 TinyMLP lab."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import numpy as np
import pytest

LAB = os.environ.get("GURUKUL_LAB", "starter")
ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = ROOT / LAB


def _load(mod_name: str):
    sys.path.insert(0, str(LAB_DIR))
    for key in list(sys.modules):
        if key.split(".")[0] == "mlp":
            del sys.modules[key]
    return importlib.import_module(mod_name)


mlp = _load("mlp")


def test_forward_fixture_yhat_0_17():
    model = mlp.TinyMLP()
    x = np.array([1.0, 2.0])
    y_hat = model.forward(x)
    assert y_hat == pytest.approx(0.17, abs=1e-9)


def test_numerical_matches_analytic_w2_grad():
    model = mlp.TinyMLP()
    x = np.array([1.0, 2.0])
    y = 0.0

    # Analytic ∂L/∂W2 for L=(ŷ-y)^2 before any update:
    h = model.hidden(x)
    y_hat = model.forward(x)
    dL_dy = 2.0 * (y_hat - y)
    analytic = dL_dy * h

    numeric = mlp.numerical_dL_dW2(model, x, y, eps=1e-6)
    assert numeric == pytest.approx(analytic, rel=1e-4, abs=1e-6)

    # train_step should move W2 along -analytic (lr=1 for easy check of delta direction)
    before = model.W2.copy()
    mlp.train_step(model, x, y, lr=0.05)
    delta = model.W2 - before
    assert np.dot(delta, -analytic) > 0


def test_train_loop_mse_drops():
    model = mlp.TinyMLP()
    x = np.array([1.0, 2.0])
    y = 0.5
    history = mlp.train_loop(model, x, y, steps=40, lr=0.1)
    assert history[-1] < history[0]
    assert history[-1] < 0.01
