"""PROD 401 — FakeJudge + human disagreement helpers (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-401/tests -q
"""

from __future__ import annotations

from typing import Sequence


VALID_MODES = frozenset({"lexical", "position_biased", "self_prefer"})


def _tokenize(text: str) -> set[str]:
    return {t for t in "".join(c.lower() if c.isalnum() else " " for c in text).split() if t}


def lexical_overlap_score(response: str, reference: str) -> float:
    """Jaccard overlap of token sets in [0, 1]. Empty reference → 0.0."""
    # TODO: validate types; tokenize; return |∩| / |∪|
    raise NotImplementedError("TODO: lexical_overlap_score")


class FakeJudge:
    """Offline judge with optional bias modes (see solution docstring)."""

    def __init__(
        self,
        mode: str = "lexical",
        *,
        bias_position: str = "A",
        self_marker: str = "[[MODEL_X]]",
    ) -> None:
        # TODO: validate mode / bias_position; store fields
        raise NotImplementedError("TODO: FakeJudge.__init__")

    def score_response(self, response: str, reference: str) -> dict[str, object]:
        """Return ``{"score": float, "label": "pass"|"fail", "mode": str}``."""
        # TODO: lexical score (+ optional self_prefer boost); pass if >= 0.5
        raise NotImplementedError("TODO: score_response")

    def pairwise(
        self,
        response_a: str,
        response_b: str,
        *,
        reference: str | None = None,
    ) -> dict[str, object]:
        """Compare A vs B. Returns winner A|B|tie plus bias metadata."""
        # TODO: branch on mode — position_biased / self_prefer / lexical
        raise NotImplementedError("TODO: pairwise")


def judge_human_disagreement(
    judge_labels: Sequence[str],
    human_labels: Sequence[str],
) -> dict[str, object]:
    """Compare judge vs human labels; recommend next steps on disagreement."""
    # TODO: agreement, disagreed_indices, recommended_next (see solution)
    raise NotImplementedError("TODO: judge_human_disagreement")
