"""FOUND-102 — log-probs and perplexity (starter)."""

from __future__ import annotations

import numpy as np


def sequence_nll(logprobs: np.ndarray | list[float]) -> float:
    """Mean negative log-likelihood from per-token log probabilities (natural log)."""
    raise NotImplementedError


def perplexity_from_logprobs(logprobs: np.ndarray | list[float]) -> float:
    """PPL = exp(mean NLL) from token logprobs."""
    raise NotImplementedError


def perplexity_from_probs(probs: np.ndarray | list[float]) -> float:
    """PPL from raw probabilities (natural log)."""
    raise NotImplementedError
