"""APP 304 — retrieval + agreement + significance metrics (solution).

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
    if k <= 0:
        raise ValueError("k must be positive")
    rel = set(relevant)
    top = _as_list(retrieved)[:k]
    if not top:
        return 0.0
    tp = sum(1 for d in top if d in rel)
    return tp / float(k)


def recall_at_k(
    retrieved: Sequence[Hashable],
    relevant: Iterable[Hashable],
    k: int,
) -> float:
    """Recall@k for binary relevance.

    R@k = |retrieved[:k] ∩ relevant| / |relevant|

    If relevant is empty → 0.0 (lab convention; avoids div-by-zero).
    """
    if k <= 0:
        raise ValueError("k must be positive")
    rel = set(relevant)
    if not rel:
        return 0.0
    top = _as_list(retrieved)[:k]
    tp = sum(1 for d in top if d in rel)
    return tp / float(len(rel))


def f1_at_k(
    retrieved: Sequence[Hashable],
    relevant: Iterable[Hashable],
    k: int,
) -> float:
    """F1@k = harmonic mean of P@k and R@k; 0 if both are 0."""
    p = precision_at_k(retrieved, relevant, k)
    r = recall_at_k(retrieved, relevant, k)
    if p + r == 0.0:
        return 0.0
    return 2.0 * p * r / (p + r)


def reciprocal_rank(
    ranked: Sequence[Hashable],
    relevant: Iterable[Hashable],
) -> float:
    """RR for one query: 1/rank of first relevant hit (1-indexed), else 0."""
    rel = set(relevant)
    if not rel:
        return 0.0
    for i, doc in enumerate(_as_list(ranked), start=1):
        if doc in rel:
            return 1.0 / float(i)
    return 0.0


def mean_reciprocal_rank(
    ranked_lists: Sequence[Sequence[Hashable]],
    relevant_sets: Sequence[Iterable[Hashable]],
) -> float:
    """MRR = mean of per-query reciprocal ranks."""
    if len(ranked_lists) != len(relevant_sets):
        raise ValueError("ranked_lists and relevant_sets must have the same length")
    if not ranked_lists:
        return 0.0
    scores = [
        reciprocal_rank(ranked, rel)
        for ranked, rel in zip(ranked_lists, relevant_sets, strict=True)
    ]
    return float(np.mean(np.asarray(scores, dtype=np.float64)))


def cohens_kappa(
    labels_a: Sequence[Label],
    labels_b: Sequence[Label],
) -> float:
    """Cohen's κ for two rater label lists of equal length.

    κ = (p_o - p_e) / (1 - p_e)
    If 1 - p_e == 0 (perfect chance agreement edge case), return 1.0 when p_o == 1 else 0.0.
    """
    a = _as_list(labels_a)
    b = _as_list(labels_b)
    if len(a) != len(b):
        raise ValueError("label lists must have equal length")
    n = len(a)
    if n == 0:
        raise ValueError("label lists must be non-empty")

    agree = sum(1 for x, y in zip(a, b, strict=True) if x == y)
    p_o = agree / float(n)

    ca = Counter(a)
    cb = Counter(b)
    labels = set(ca) | set(cb)
    p_e = sum((ca[lab] / n) * (cb[lab] / n) for lab in labels)

    denom = 1.0 - p_e
    if denom == 0.0:
        return 1.0 if p_o == 1.0 else 0.0
    return (p_o - p_e) / denom


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
    yt = _as_list(y_true)
    pa = _as_list(pred_a)
    pb = _as_list(pred_b)
    if not (len(yt) == len(pa) == len(pb)):
        raise ValueError("y_true, pred_a, pred_b must have equal length")
    if not yt:
        raise ValueError("inputs must be non-empty")

    b = c = 0
    for t, a, bb in zip(yt, pa, pb, strict=True):
        ok_a = a == t
        ok_b = bb == t
        if (not ok_a) and ok_b:
            b += 1
        elif ok_a and (not ok_b):
            c += 1

    disc = b + c
    if disc == 0:
        stat = 0.0
        p_value = 1.0
    else:
        stat = (b - c) ** 2 / float(disc)
        # Chi-square survival function, 1 df: P(X > stat) = erfc(sqrt(stat/2))
        p_value = float(math.erfc(math.sqrt(stat / 2.0)))

    return {
        "b": b,
        "c": c,
        "n_discordant": disc,
        "statistic": float(stat),
        "p_value": float(p_value),
    }


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
    a = np.asarray(list(scores_a), dtype=np.float64)
    b = np.asarray(list(scores_b), dtype=np.float64)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("scores_a and scores_b must be 1-D and same length")
    n = int(a.shape[0])
    if n == 0:
        raise ValueError("score vectors must be non-empty")
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")
    if alternative not in {"greater", "two-sided"}:
        raise ValueError("alternative must be 'greater' or 'two-sided'")

    observed = float(np.mean(b - a))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_bootstrap, n))
    deltas = np.mean(b[idx] - a[idx], axis=1)

    if alternative == "greater":
        p = float(np.mean(deltas <= 0.0))
    else:
        p = float(np.mean(np.abs(deltas) >= abs(observed)))

    return {
        "observed_delta": observed,
        "p_value": p,
        "n_bootstrap": int(n_bootstrap),
    }
