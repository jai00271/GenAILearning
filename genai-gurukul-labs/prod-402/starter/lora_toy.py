"""PROD 402 — toy LoRA adapter math (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-402/tests -q
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
    """Return ``scale * (B @ A)`` with rank shape checks."""
    # TODO
    raise NotImplementedError("TODO: lora_delta")


def apply_lora(
    W: np.ndarray | Sequence[Sequence[float]],
    A: np.ndarray | Sequence[Sequence[float]],
    B: np.ndarray | Sequence[Sequence[float]],
    *,
    scale: float = 1.0,
) -> np.ndarray:
    """Return ``W + scale * (B @ A)``."""
    # TODO
    raise NotImplementedError("TODO: apply_lora")


def lora_param_count(in_dim: int, out_dim: int, rank: int) -> dict[str, int]:
    """Compare full FT params vs LoRA A+B params."""
    # TODO
    raise NotImplementedError("TODO: lora_param_count")


def toy_preference_update(
    base_scores: Sequence[float],
    preferred_idx: int,
    *,
    step: float = 0.1,
) -> list[float]:
    """Boost preferred index; mildly decay others."""
    # TODO
    raise NotImplementedError("TODO: toy_preference_update")


def finetune_metric_comparison(
    before: Mapping[str, float],
    after: Mapping[str, float],
) -> dict[str, object]:
    """Compare demo/golden (and optional preference_margin) before vs after."""
    # TODO
    raise NotImplementedError("TODO: finetune_metric_comparison")
