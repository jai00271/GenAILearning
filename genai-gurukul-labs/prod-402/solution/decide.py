"""PROD 402 — FT vs RAG vs prompting decision helper (solution).

Uses eval evidence + risk flags. Teaching decision function, not a product
recommendation engine.
"""

from __future__ import annotations

from typing import Any, Mapping


VALID_CHOICES = frozenset({"prompting", "rag", "finetune"})


def _f(evidence: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    val = evidence.get(key, default)
    return float(val)


def _b(evidence: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(evidence.get(key, default))


def recommend_adaptation(evidence: Mapping[str, Any]) -> dict[str, object]:
    """Recommend prompting | rag | finetune from eval-shaped evidence.

    Expected keys (all optional with defaults):
      prompting_score, rag_score, ft_score : float in [0, 1]
      data_available : bool — labeled adaptation data exists
      eval_leakage_risk : bool — train/eval contamination suspected
      catastrophic_forgetting_delta : float — golden drop after FT (>=0 means drop)
      demo_score, golden_score : float — catch "demo better, golden worse"
      knowledge_needs_refresh : bool — facts change often (favors RAG)

    Policy (teaching, labeled simplification):
      1. If demo_score >> golden_score (≥0.15 gap) → do not trust FT/demo; prefer
         prompting or rag based on scores, and flag demo_better_golden_worse.
      2. If eval_leakage_risk → never recommend finetune; prefer best of prompting/rag.
      3. If knowledge_needs_refresh → finetune ineligible (don't bake churning facts);
         prefer rag when rag_score >= prompting_score - 0.05.
      4. Else pick the max of eligible scores; finetune requires data_available
         and catastrophic_forgetting_delta <= 0.05.
      5. Ties break: prompting > rag > finetune (cheapest first).
    """
    if not isinstance(evidence, Mapping):
        raise TypeError("evidence must be a mapping")

    p = _f(evidence, "prompting_score", 0.0)
    r = _f(evidence, "rag_score", 0.0)
    f = _f(evidence, "ft_score", 0.0)
    data_ok = _b(evidence, "data_available", False)
    leak = _b(evidence, "eval_leakage_risk", False)
    forget = _f(evidence, "catastrophic_forgetting_delta", 0.0)
    demo = _f(evidence, "demo_score", 0.0)
    golden = _f(evidence, "golden_score", demo if "demo_score" not in evidence else _f(evidence, "golden_score", 0.0))
    # Fix golden default: if golden_score absent, use demo (no gap)
    if "golden_score" not in evidence:
        golden = demo
    refresh = _b(evidence, "knowledge_needs_refresh", False)

    flags: list[str] = []
    defense: list[str] = []

    demo_gap = demo - golden
    demo_better_golden_worse = demo_gap >= 0.15
    if demo_better_golden_worse:
        flags.append("demo_better_golden_worse")
        defense.append(
            "Demo metric exceeds golden by ≥0.15 — treat FT/demo wins as untrusted until golden recovers."
        )

    if leak:
        flags.append("eval_leakage_risk")
        defense.append("Eval leakage risk set — refuse fine-tune until splits are cleaned.")

    if forget > 0.05:
        flags.append("catastrophic_forgetting")
        defense.append(
            f"Catastrophic forgetting delta={forget:.2f} > 0.05 — FT blocked until golden holds."
        )

    # Candidate scores with constraints
    scores = {"prompting": p, "rag": r, "finetune": f}
    eligible = {"prompting": True, "rag": True, "finetune": True}

    if leak or not data_ok or forget > 0.05 or demo_better_golden_worse or refresh:
        eligible["finetune"] = False
        if not data_ok and "no_ft_data" not in flags:
            flags.append("no_ft_data")
            defense.append("No labeled adaptation data — fine-tune ineligible.")

    if refresh:
        flags.append("knowledge_needs_refresh")
        defense.append("Knowledge refresh needed — prefer RAG over baking facts into weights.")

    # Pick best eligible
    order = ["prompting", "rag", "finetune"]  # default tie-break: cheapest first
    best = None
    best_score = float("-inf")
    for name in order:
        if not eligible[name]:
            continue
        if scores[name] > best_score:
            best_score = scores[name]
            best = name

    # Under knowledge churn, prefer RAG when it is within 0.05 of prompting.
    if (
        refresh
        and eligible.get("rag")
        and r >= (p - 0.05)
        and best in {"prompting", "rag"}
    ):
        best = "rag"
        best_score = scores["rag"]

    if best is None:
        best = "prompting"
        defense.append("No eligible option after gates — fall back to prompting.")

    if best == "prompting":
        defense.append("Prompting wins on evidence and/or cost-first tie-break.")
    elif best == "rag":
        defense.append("RAG wins on evidence (retrieval beats weight updates for this slice).")
    else:
        defense.append(
            "Fine-tune wins on held-out scores with data available and forgetting under threshold."
        )

    return {
        "recommendation": best,
        "scores": {"prompting": p, "rag": r, "finetune": f},
        "eligible": eligible,
        "flags": flags,
        "defense": defense,
        "demo_better_golden_worse": demo_better_golden_worse,
        "demo_gap": float(demo_gap),
    }


def compare_demo_vs_golden(demo_score: float, golden_score: float, *, gap: float = 0.15) -> dict[str, object]:
    """Flag the classic 'demo better, golden worse' failure mode."""
    if gap <= 0:
        raise ValueError("gap must be positive")
    d = float(demo_score) - float(golden_score)
    return {
        "demo_score": float(demo_score),
        "golden_score": float(golden_score),
        "gap": float(d),
        "demo_better_golden_worse": d >= gap,
        "threshold": float(gap),
    }
