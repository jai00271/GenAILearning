"""PROD 401 — FakeJudge + human disagreement helpers (solution).

Deterministic offline stand-in for LLM-as-judge. Demonstrates lexical scoring,
position bias, and self-preference — teaching tripwires, not production judges.
"""

from __future__ import annotations

from collections import Counter
from typing import Sequence


VALID_MODES = frozenset({"lexical", "position_biased", "self_prefer"})


def _tokenize(text: str) -> set[str]:
    return {t for t in "".join(c.lower() if c.isalnum() else " " for c in text).split() if t}


def lexical_overlap_score(response: str, reference: str) -> float:
    """Jaccard overlap of token sets in [0, 1]. Empty reference → 0.0."""
    if not isinstance(response, str) or not isinstance(reference, str):
        raise TypeError("response and reference must be strings")
    ref_toks = _tokenize(reference)
    if not ref_toks:
        return 0.0
    resp_toks = _tokenize(response)
    if not resp_toks:
        return 0.0
    inter = len(resp_toks & ref_toks)
    union = len(resp_toks | ref_toks)
    return inter / float(union) if union else 0.0


class FakeJudge:
    """Offline judge with optional bias modes.

    Modes
    -----
    lexical
        Score = lexical overlap with reference; pairwise picks higher overlap
        vs a shared reference when provided, else longer response (tie → "tie").
    position_biased
        Pairwise always prefers ``bias_position`` ("A" or "B") regardless of
        content — teaching stand-in for position bias (Zheng et al.).
    self_prefer
        Pairwise prefers the response containing ``self_marker`` — teaching
        stand-in for self-enhancement / self-preference bias.
    """

    def __init__(
        self,
        mode: str = "lexical",
        *,
        bias_position: str = "A",
        self_marker: str = "[[MODEL_X]]",
    ) -> None:
        if mode not in VALID_MODES:
            raise ValueError(f"mode must be one of {sorted(VALID_MODES)}")
        if bias_position not in {"A", "B"}:
            raise ValueError("bias_position must be 'A' or 'B'")
        self.mode = mode
        self.bias_position = bias_position
        self.self_marker = self_marker

    def score_response(self, response: str, reference: str) -> dict[str, object]:
        """Return ``{"score": float, "label": "pass"|"fail", "mode": str}``.

        Pass threshold: score >= 0.5.
        """
        score = lexical_overlap_score(response, reference)
        # self_prefer mode boosts score if marker present (mild self-boost demo)
        if self.mode == "self_prefer" and self.self_marker in response:
            score = min(1.0, score + 0.25)
        label = "pass" if score >= 0.5 else "fail"
        return {"score": float(score), "label": label, "mode": self.mode}

    def pairwise(
        self,
        response_a: str,
        response_b: str,
        *,
        reference: str | None = None,
    ) -> dict[str, object]:
        """Compare A vs B. Returns winner A|B|tie plus bias metadata."""
        if not isinstance(response_a, str) or not isinstance(response_b, str):
            raise TypeError("responses must be strings")

        if self.mode == "position_biased":
            return {
                "winner": self.bias_position,
                "biased": True,
                "bias_kind": "position",
                "score_a": None,
                "score_b": None,
            }

        if self.mode == "self_prefer":
            a_has = self.self_marker in response_a
            b_has = self.self_marker in response_b
            if a_has and not b_has:
                winner = "A"
            elif b_has and not a_has:
                winner = "B"
            elif reference is not None:
                sa = lexical_overlap_score(response_a, reference)
                sb = lexical_overlap_score(response_b, reference)
                winner = "A" if sa > sb else ("B" if sb > sa else "tie")
            else:
                winner = "tie"
            return {
                "winner": winner,
                "biased": a_has or b_has,
                "bias_kind": "self_preference",
                "score_a": None,
                "score_b": None,
            }

        # lexical
        if reference is not None:
            sa = lexical_overlap_score(response_a, reference)
            sb = lexical_overlap_score(response_b, reference)
        else:
            sa = float(len(response_a.strip()))
            sb = float(len(response_b.strip()))
        if sa > sb:
            winner = "A"
        elif sb > sa:
            winner = "B"
        else:
            winner = "tie"
        return {
            "winner": winner,
            "biased": False,
            "bias_kind": None,
            "score_a": float(sa),
            "score_b": float(sb),
        }


def judge_human_disagreement(
    judge_labels: Sequence[str],
    human_labels: Sequence[str],
) -> dict[str, object]:
    """Compare judge vs human labels of equal length.

    Returns agreement rate, disagreed indices, and ``recommended_next`` actions
    when disagreement is material (agreement < 0.8).
    """
    j = list(judge_labels)
    h = list(human_labels)
    if len(j) != len(h):
        raise ValueError("judge_labels and human_labels must have equal length")
    if not j:
        return {
            "n": 0,
            "agreement": 1.0,
            "disagreed_indices": [],
            "recommended_next": ["collect_more_labels"],
        }

    disagreed = [i for i, (a, b) in enumerate(zip(j, h, strict=True)) if a != b]
    agreement = 1.0 - (len(disagreed) / float(len(j)))

    if agreement >= 0.8:
        next_steps = ["spot_check_sample", "continue_with_judge_plus_audit"]
    else:
        next_steps = [
            "pause_auto_ship",
            "adjudicate_disagreements_with_humans",
            "inspect_judge_rubric_and_bias",
            "recalibrate_or_replace_judge",
            "expand_golden_set_on_failure_slices",
        ]

    # Surface which labels dominate disagreements (teaching signal)
    mismatch_pairs = Counter((j[i], h[i]) for i in disagreed)

    return {
        "n": len(j),
        "agreement": float(agreement),
        "disagreed_indices": disagreed,
        "mismatch_pairs": {f"{a}->{b}": c for (a, b), c in mismatch_pairs.items()},
        "recommended_next": next_steps,
    }
