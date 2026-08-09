"""PROD 402 — toy LoRA adapter math + tiny preference/finetune metric compare (solution).

No model downloads. Simulates W' = W + scale * (B @ A) and a tiny update step.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


def lora_delta(
    A: np.ndarray | Sequence[Sequence[float]],
    B: np.ndarray | Sequence[Sequence[float]],
    *,
    scale: float = 1.0,
) -> np.ndarray:
    """Return ``scale * (B @ A)``.

    Convention (Hu et al. LoRA teaching shape):
      A has shape (r, in_dim), B has shape (out_dim, r),
      so B @ A has shape (out_dim, in_dim) matching W.
    """
    a = np.asarray(A, dtype=np.float64)
    b = np.asarray(B, dtype=np.float64)
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("A and B must be 2-D")
    if b.shape[1] != a.shape[0]:
        raise ValueError(
            f"incompatible LoRA ranks: B is {b.shape}, A is {a.shape} (need B.shape[1]==A.shape[0])"
        )
    return float(scale) * (b @ a)


def apply_lora(
    W: np.ndarray | Sequence[Sequence[float]],
    A: np.ndarray | Sequence[Sequence[float]],
    B: np.ndarray | Sequence[Sequence[float]],
    *,
    scale: float = 1.0,
) -> np.ndarray:
    """Return ``W + scale * (B @ A)`` with shape checks."""
    w = np.asarray(W, dtype=np.float64)
    delta = lora_delta(A, B, scale=scale)
    if w.shape != delta.shape:
        raise ValueError(f"W shape {w.shape} != LoRA delta shape {delta.shape}")
    return w + delta


def lora_param_count(in_dim: int, out_dim: int, rank: int) -> dict[str, int]:
    """Compare full fine-tune params vs LoRA (A + B only)."""
    if in_dim <= 0 or out_dim <= 0 or rank <= 0:
        raise ValueError("in_dim, out_dim, rank must be positive")
    full = in_dim * out_dim
    lora = rank * in_dim + out_dim * rank
    return {
        "full_ft_params": full,
        "lora_params": lora,
        "rank": rank,
        "saved_params": full - lora,
    }


def toy_preference_update(
    base_scores: Sequence[float],
    preferred_idx: int,
    *,
    step: float = 0.1,
) -> list[float]:
    """Tiny teaching update: boost preferred candidate, mildly decay others.

    Simulates a preference/finetune step on scalar utilities — not real gradients.
    """
    scores = [float(x) for x in base_scores]
    if not scores:
        raise ValueError("base_scores must be non-empty")
    if preferred_idx < 0 or preferred_idx >= len(scores):
        raise ValueError("preferred_idx out of range")
    if step <= 0:
        raise ValueError("step must be positive")
    updated = []
    for i, s in enumerate(scores):
        if i == preferred_idx:
            updated.append(s + step)
        else:
            updated.append(s - step * 0.25)
    return updated


def finetune_metric_comparison(
    before: Mapping[str, float],
    after: Mapping[str, float],
) -> dict[str, object]:
    """Compare before/after metrics; surface forgetting on held-out keys.

    ``before`` / ``after`` should include at least ``demo`` and ``golden``.
    Optional ``preference_margin``.
    """
    b = dict(before)
    a = dict(after)
    for key in ("demo", "golden"):
        if key not in b or key not in a:
            raise KeyError(f"missing metric '{key}'")

    demo_delta = float(a["demo"]) - float(b["demo"])
    golden_delta = float(a["golden"]) - float(b["golden"])
    forgetting = golden_delta < 0
    demo_better_golden_worse = float(a["demo"]) > float(a["golden"]) and golden_delta < 0

    out: dict[str, object] = {
        "demo_delta": demo_delta,
        "golden_delta": golden_delta,
        "forgetting": forgetting,
        "demo_better_golden_worse": demo_better_golden_worse,
        "before": {k: float(b[k]) for k in b},
        "after": {k: float(a[k]) for k in a},
    }
    if "preference_margin" in b and "preference_margin" in a:
        out["preference_margin_delta"] = float(a["preference_margin"]) - float(
            b["preference_margin"]
        )
    return out
