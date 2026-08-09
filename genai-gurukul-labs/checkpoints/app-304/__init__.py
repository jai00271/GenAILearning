"""Known-good APP 304 checkpoint — frozen eval helpers for APP 305 / later modules.

Import pattern (from a lab under genai-gurukul-labs/):

    import sys
    from pathlib import Path
    CHECKPOINT = Path(__file__).resolve().parents[N] / "checkpoints" / "app-304"
    sys.path.insert(0, str(CHECKPOINT))
    from metrics import precision_at_k, recall_at_k, f1_at_k, mean_reciprocal_rank
    from golden import load_golden_jsonl, find_leakage

Prefer this package over a learner's possibly-wrong `app-304/starter` unless
`GURUKUL_LAB=solution pytest app-304/tests -q` (or the learner's own green run)
has passed and the team explicitly opts into that code.
"""

from golden import find_leakage, golden_questions, load_golden_jsonl, normalize_text
from metrics import (
    cohens_kappa,
    f1_at_k,
    mean_reciprocal_rank,
    mcnemar_contingency,
    paired_bootstrap_pvalue,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

__all__ = [
    "cohens_kappa",
    "f1_at_k",
    "find_leakage",
    "golden_questions",
    "load_golden_jsonl",
    "mcnemar_contingency",
    "mean_reciprocal_rank",
    "normalize_text",
    "paired_bootstrap_pvalue",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
]

__version__ = "304.0.0"
