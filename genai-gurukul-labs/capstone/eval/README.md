# Golden set — Ops Incident Copilot

**Bar:** ≥ 40 labeled Q&A · **Recall@5 ≥ 0.60** on frozen labels  
**File:** `golden_set.jsonl` (one JSON object per line)

## Schema

```json
{
  "id": "q001",
  "query": "...",
  "relevant_doc_ids": ["runbook-auth-crashloop"],
  "notes": "optional labeling note",
  "answer_key": "optional short expected gist"
}
```

## Protocol (state this in `writeups/eval_report.md`)

1. Freeze corpus commit + chunking config before labeling.
2. Label `relevant_doc_ids` for retrieval eval (document or chunk IDs — be consistent).
3. Run retriever; compute Recall@5 = fraction of queries with ≥1 relevant id in top-5.
4. Pass only if Recall@5 ≥ 0.60 on this frozen set (or a declared superseding freeze).

Items `q001`–`q040` are **synthetic placeholders** aligned to the three fixtures plus
generic ops themes. Replace/extend labels as you expand the corpus.
