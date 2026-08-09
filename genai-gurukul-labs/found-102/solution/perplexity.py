"""FOUND-102 — log-probs and perplexity (solution)."""

from __future__ import annotations

import numpy as np


def sequence_nll(logprobs: np.ndarray | list[float]) -> float:
    """Mean negative log-likelihood from per-token log probabilities (natural log)."""
    lp = np.asarray(logprobs, dtype=float).ravel()
    if lp.size == 0:
        raise ValueError("logprobs must be non-empty")
    return float(np.mean(-lp))


def perplexity_from_logprobs(logprobs: np.ndarray | list[float]) -> float:
    """PPL = exp(mean NLL) from token logprobs."""
    return float(np.exp(sequence_nll(logprobs)))


def perplexity_from_probs(probs: np.ndarray | list[float]) -> float:
    """PPL from raw probabilities (natural log)."""
    p = np.asarray(probs, dtype=float).ravel()
    if np.any(p <= 0):
        raise ValueError("probabilities must be positive")
    return perplexity_from_logprobs(np.log(p))
