# APP 305 — RAG Deep-Dive

Companion lab for `genai-gurukul/modules/app-305-rag.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution .venv/bin/pytest app-305/tests -q
# after filling starter TODOs:
# GURUKUL_LAB=starter .venv/bin/pytest app-305/tests -q
```

Offline only — text/markdown fixtures, fake PDF-table string parser, CORE 204
`LocalEmbedder`, APP 304 Precision/Recall@k. No paid APIs. No real PDF binaries.

| Path | Role |
|---|---|
| `starter/` · `solution/` | ingest · chunk · retrieve |
| `tests/fixtures/` | messy table, OCR junk, markdown runbooks, golden JSONL |
| `decision-lab/README.md` | English constraints + 4-dimension rubric (portfolio memo) |
| `../debug-labs/A-broken-rag/` | separate debug lab (wrong answers; no solution) |
| `../checkpoints/app-305/` | optional known-good chunk+retrieve helpers |

## Eval beat (lab gate)

- **Metric:** macro Recall@3 (primary), Precision@3 (secondary) via `checkpoints/app-304`
- **Data:** `tests/fixtures/golden.jsonl` over the local fixture corpus
- **Pass/fail:** Recall@3 ≥ 0.75 and Precision@3 ≥ 0.25 on structure-aware + hybrid retrieve
