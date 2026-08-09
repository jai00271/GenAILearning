# Debug Lab A — Broken RAG

**Module link:** APP 305 · [`app-305-rag.html`](../../../genai-gurukul/modules/app-305-rag.html)  
**Kind:** debug fixture · **no TODO markers** · **no adjacent solution**

This folder ships a small retrieval stack that **runs cleanly** and still returns
**wrong answers** on the included queries. Your job is root-cause analysis, not
filling stubs.

## Run

```bash
cd genai-gurukul-labs
source .venv/bin/activate
python debug-labs/A-broken-rag/broken_rag.py
```

Expected: the script prints confident answers that disagree with `queries.jsonl`
`expected_doc_id` / `expected_contains` fields.

## RCA checklist (short)

1. Diff **ingestion** — which files are loaded? Is OCR junk treated as trusted?
2. Diff **chunking** — are leave-policy table rows split mid-row?
3. Diff **retrieval** — semantic-only? keyword-only? inverted scores?
4. Write a 5–10 line English note: *defect → evidence → fix hypothesis*.
5. Optional: patch locally; do **not** expect a `solution/` folder here.

Withheld: the intentional defects are not labeled in code comments. Discover them
with the checklist and by comparing behavior to the convergent APP 305 lab.
