"""Convergent checks for CORE 203."""

from __future__ import annotations

import importlib
import math
import os
import sys
from pathlib import Path

import pytest

LAB = os.environ.get("GURUKUL_LAB", "starter")
ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = ROOT / LAB


def _load(mod_name: str):
    sys.path.insert(0, str(LAB_DIR))
    for key in list(sys.modules):
        base = key.split(".")[0]
        if base in {"pretrain_loss", "preference"}:
            del sys.modules[key]
    return importlib.import_module(mod_name)


pretrain_loss = _load("pretrain_loss")
preference = _load("preference")


def test_mean_nll_and_perplexity_worked_example():
    # Same geometric fixture as FOUND 102: p = [0.5, 0.25, 0.125] → PPL = 4
    probs = [0.5, 0.25, 0.125]
    logprobs = [math.log(p) for p in probs]
    assert pretrain_loss.mean_nll(logprobs) == pytest.approx(math.log(4.0))
    assert pretrain_loss.perplexity_from_logprobs(logprobs) == pytest.approx(4.0)


def test_mean_nll_rejects_empty():
    with pytest.raises(ValueError):
        pretrain_loss.mean_nll([])


def test_preference_margin_sign():
    assert preference.preference_margin(-1.0, -3.0) == pytest.approx(2.0)
    assert preference.preference_margin(-4.0, -1.0) < 0


def test_dpo_style_loss_prefers_chosen():
    # Strong chosen advantage → loss near 0
    low = preference.dpo_style_loss(-1.0, -5.0, beta=1.0)
    high = preference.dpo_style_loss(-5.0, -1.0, beta=1.0)
    assert low < 0.05
    assert high > 1.0
    assert low < high


def test_dpo_style_loss_with_reference():
    # Equal policy margins relative to reference → delta 0 → loss = log(2)
    loss = preference.dpo_style_loss(
        logprob_chosen=-2.0,
        logprob_rejected=-4.0,
        logprob_ref_chosen=-1.0,
        logprob_ref_rejected=-3.0,
        beta=1.0,
    )
    # ( -2 - (-1) ) - ( -4 - (-3) ) = (-1) - (-1) = 0
    assert loss == pytest.approx(math.log(2.0))


def test_dpo_style_loss_beta_scales():
    base = preference.dpo_style_loss(-1.0, -2.0, beta=1.0)
    sharper = preference.dpo_style_loss(-1.0, -2.0, beta=2.0)
    # Larger beta amplifies a positive margin → smaller loss
    assert sharper < base


def test_dpo_rejects_nonpositive_beta():
    with pytest.raises(ValueError):
        preference.dpo_style_loss(-1.0, -2.0, beta=0.0)
