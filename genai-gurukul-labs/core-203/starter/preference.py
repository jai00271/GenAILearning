"""CORE 203 — toy DPO-style preference loss (starter)."""

from __future__ import annotations


def dpo_style_loss(
    logprob_chosen: float,
    logprob_rejected: float,
    *,
    logprob_ref_chosen: float = 0.0,
    logprob_ref_rejected: float = 0.0,
    beta: float = 1.0,
) -> float:
    """Toy DPO-style loss term (scalar, teaching scale).

    Computes::

        delta = beta * (
            (logprob_chosen - logprob_ref_chosen)
            - (logprob_rejected - logprob_ref_rejected)
        )
        loss = -log(sigmoid(delta))

    where ``sigmoid(z) = 1 / (1 + exp(-z))``.

    ``logprob_*`` values are **sequence log-prob sums** (natural log), not mean NLL.

    Simplification (labeled): default reference log-probs are 0.0 so the margin
    collapses to ``beta * (logprob_chosen - logprob_rejected)``. Production DPO
    keeps a real reference policy; do not drop it casually outside this lab.
    """
    raise NotImplementedError


def preference_margin(logprob_chosen: float, logprob_rejected: float) -> float:
    """Return chosen − rejected sequence log-prob sum (positive ⇒ prefers chosen)."""
    raise NotImplementedError
