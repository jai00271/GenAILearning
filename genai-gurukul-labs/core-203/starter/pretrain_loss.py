"""CORE 203 — pretraining loss metrics from token log-probs (starter).

Reimplements FOUND 102 concepts locally for this module (do not import found-102).
"""

from __future__ import annotations

from collections.abc import Sequence


def mean_nll(logprobs: Sequence[float]) -> float:
    """Mean negative log-likelihood from per-token log probabilities (natural log).

    mean_nll = average_i[ -logprobs[i] ]
    """
    raise NotImplementedError


def perplexity_from_logprobs(logprobs: Sequence[float]) -> float:
    """Perplexity = exp(mean NLL) from token log-probs (natural log)."""
    raise NotImplementedError
