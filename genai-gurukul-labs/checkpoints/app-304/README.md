# Checkpoint · APP 304 — Evaluation Fundamentals

**Known-good** frozen metric + golden-set helpers for later modules (especially
**APP 305 RAG**). Later labs should import from this checkpoint **by default**,
not from a learner's possibly-wrong `app-304/starter` code.

## What is frozen here

| Symbol | Role |
|---|---|
| `load_golden_jsonl` | JSONL golden loader (`id`, `question`, `relevant_ids`) |
| `find_leakage` | Normalized overlap check: train/prompt texts vs eval questions |
| `normalize_text` | Leakage normalization helper |
| `precision_at_k` / `recall_at_k` / `f1_at_k` | Binary relevance @ k |
| `reciprocal_rank` / `mean_reciprocal_rank` | Ranking MRR |
| `cohens_kappa` | Two-rater agreement |
| `mcnemar_contingency` | Paired binary discordant-cell helper (71→74 style) |
| `paired_bootstrap_pvalue` | Paired mean-difference bootstrap p-value intuition |

These are **teaching implementations** (pure Python / NumPy). Prefer sklearn /
scipy in production papers when you need every edge-case flag — but keep this
checkpoint for offline RAG plumbing tests.

## How APP 305 should import

From a file under `genai-gurukul-labs/app-305/...` (adjust `parents[N]` to reach
the labs root):

```python
import sys
from pathlib import Path

LABS_ROOT = Path(__file__).resolve().parents[2]  # tune depth as needed
CHECKPOINT = LABS_ROOT / "checkpoints" / "app-304"
sys.path.insert(0, str(CHECKPOINT))

from metrics import precision_at_k, recall_at_k, f1_at_k, mean_reciprocal_rank
from golden import load_golden_jsonl, find_leakage
```

## Eval beat reminder

Every RAG change should declare **metric / data / pass-fail** before claiming a
win. Use these helpers for the metric box; keep goldens versioned; gate ships
with a paired test when deltas are small (71→74).

## Version

`__version__ = "304.0.0"` — bump only if APP 305 / capstone contracts change deliberately.
