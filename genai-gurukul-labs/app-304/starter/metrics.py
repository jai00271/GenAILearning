"""APP 304 — retrieval + agreement + significance metrics (starter).

Pure Python / NumPy. Formulas follow classic IR / sklearn identities (see lesson citations).
Simplifications are labeled in docstrings.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Hashable, Iterable, Sequence

import numpy as np

Label = Hashable


def _as_list(seq: Sequence) -> list:
    return list(seq)


def precision_at_k(
    retrieved: Sequence[Hashable],
    relevant: Iterable[Hashable],
    k: int,
) -> float:
    """Precision@k for binary relevance.

    P@k = |retrieved[:k] ∩ relevant| / k

    If k <= 0 → ValueError. Empty retrieved with k>0 → 0.0.
    Denominator is always k (IR convention for P@k), even if fewer than k docs returned.
    """
    # TODO: implement precision_at_k
    raise NotImplementedError


def recall_at_k(
    retrieved: Sequence[Hashable],
    relevant: Iterable[Hashable],
    k: int,
) -> float:
    """Recall@k for binary relevance.

    R@k = |retrieved[:k] ∩ relevant| / |relevant|

    If relevant is empty → 0.0 (lab convention; avoids div-by-zero).
    """
    # TODO: implement recall_at_k
    raise NotImplementedError


def f1_at_k(
    retrieved: Sequence[Hashable],
    relevant: Iterable[Hashable],
    k: int,
) -> float:
    """F1@k = harmonic mean of P@k and R@k; 0 if both are 0."""
    # TODO: implement f1_at_k
    raise NotImplementedError


def reciprocal_rank(
    ranked: Sequence[Hashable],
    relevant: Iterable[Hashable],
) -> float:
    """RR for one query: 1/rank of first relevant hit (1-indexed), else 0."""
    # TODO: implement reciprocal_rank
    raise NotImplementedError


def mean_reciprocal_rank(
    ranked_lists: Sequence[Sequence[Hashable]],
    relevant_sets: Sequence[Iterable[Hashable]],
) -> float:
    """MRR = mean of per-query reciprocal ranks."""
    # TODO: implement mean_reciprocal_rank
    raise NotImplementedError


def cohens_kappa(
    labels_a: Sequence[Label],
    labels_b: Sequence[Label],
) -> float:
    """Cohen's κ for two rater label lists of equal length.

    κ = (p_o - p_e) / (1 - p_e)
    If 1 - p_e == 0 (perfect chance agreement edge case), return 1.0 when p_o == 1 else 0.0.
    """
    # TODO: implement cohens_kappa
    raise NotImplementedError


def mcnemar_contingency(
    y_true: Sequence[Label],
    pred_a: Sequence[Label],
    pred_b: Sequence[Label],
) -> dict[str, float | int]:
    """McNemar-style discordant contingency for paired binary correctness.

    Builds correctness vectors cA = (pred_a == y_true), cB = (pred_b == y_true), then:
      b = count(A wrong, B right)
      c = count(A right, B wrong)

    Returns dict with b, c, n_discordant, statistic = (b-c)^2 / (b+c) (0 if b+c==0),
    and a simple two-sided p-value via chi-square survival with 1 df (no continuity
    correction — labeled simplification).

    Reference framing: McNemar's test on paired nominal data (discordant cells).
    """
    # TODO: implement mcnemar_contingency
    raise NotImplementedError


def paired_bootstrap_pvalue(
    scores_a: Sequence[float],
    scores_b: Sequence[float],
    *,
    n_bootstrap: int = 5000,
    seed: int = 0,
    alternative: str = "greater",
) -> dict[str, float | int]:
    """Paired bootstrap p-value intuition for mean(scores_b - scores_a).

    Resample item indices with replacement; each replicate Δ* = mean(sB* - sA*).

    alternative:
      - "greater": H1 mean(B-A) > 0 → one-sided p ≈ fraction of Δ* <= 0
      - "two-sided": fraction of |Δ*| >= |observed Δ|

    Returns observed_delta, p_value, n_bootstrap.

    Teaching helper — not a full BCa interval. For 71→74 style: pass per-item 0/1
    correctness under system A and B.
    """
    # TODO: implement paired_bootstrap_pvalue
    raise NotImplementedError
