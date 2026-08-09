"""PROD 402 — FT vs RAG vs prompting decision helper (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-402/tests -q
"""

from __future__ import annotations

from typing import Any, Mapping


VALID_CHOICES = frozenset({"prompting", "rag", "finetune"})


def recommend_adaptation(evidence: Mapping[str, Any]) -> dict[str, object]:
    """Recommend prompting | rag | finetune from eval-shaped evidence."""
    # TODO: implement policy from lesson / solution docstring
    raise NotImplementedError("TODO: recommend_adaptation")


def compare_demo_vs_golden(
    demo_score: float, golden_score: float, *, gap: float = 0.15
) -> dict[str, object]:
    """Flag 'demo better, golden worse' when demo - golden >= gap."""
    # TODO
    raise NotImplementedError("TODO: compare_demo_vs_golden")
