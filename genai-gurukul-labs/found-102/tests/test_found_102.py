"""Tests for FOUND-102 labs."""

from __future__ import annotations

import importlib
import math
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
        base = key.split(".")[0]
        if base in {"geometry", "softmax", "perplexity"}:
            del sys.modules[key]
    return importlib.import_module(mod_name)


geometry = _load("geometry")
softmax_mod = _load("softmax")
perplexity = _load("perplexity")


def test_dot_and_norm():
    assert geometry.dot([1, 2, 3], [4, 5, 6]) == pytest.approx(32.0)
    assert geometry.l2_norm([3, 4]) == pytest.approx(5.0)


def test_cosine_wiki_style():
    q = [1.0, 0.8, 0.1]
    a = [0.9, 0.7, 0.0]
    b = [0.1, 0.0, 0.9]
    assert geometry.cosine(q, a) > geometry.cosine(q, b)


def test_softmax_sums_to_one():
    p = softmax_mod.softmax([2.0, 1.0, 0.1], temperature=1.0)
    assert p.sum() == pytest.approx(1.0)
    assert p[0] == pytest.approx(0.65900114, rel=1e-5)


def test_softmax_temperature_flattens():
    sharp = softmax_mod.softmax([2.0, 1.0, 0.1], temperature=1.0)
    flat = softmax_mod.softmax([2.0, 1.0, 0.1], temperature=2.0)
    assert flat[0] < sharp[0]
    assert flat[2] > sharp[2]


def test_softmax_rejects_nonpositive_temperature():
    with pytest.raises(ValueError):
        softmax_mod.softmax([1.0, 2.0], temperature=0.0)


def test_perplexity_worked_example():
    probs = [0.5, 0.25, 0.125]
    logprobs = [math.log(p) for p in probs]
    assert perplexity.sequence_nll(logprobs) == pytest.approx(math.log(4.0))
    assert perplexity.perplexity_from_logprobs(logprobs) == pytest.approx(4.0)
    assert perplexity.perplexity_from_probs(probs) == pytest.approx(4.0)
