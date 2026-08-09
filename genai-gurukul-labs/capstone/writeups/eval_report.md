# Eval report — Ops Incident Copilot (template)

**Status:** TEMPLATE — replace placeholders with measured values  
**Golden set:** `../eval/golden_set.jsonl` (≥40 required)  
**Pass bar:** Recall@5 ≥ 0.60 on frozen labels

## 1. Protocol

| Field | Value |
|-------|-------|
| Corpus freeze (commit / date) | _TBD_ |
| Chunking config | _TBD_ |
| Embedder / index | _TBD_ |
| `k` | 5 |
| Label unit | document ids (e.g. `runbook-auth-crashloop`) |
| N queries | _must be ≥ 40_ |

**Recall@5 definition:** fraction of queries for which at least one id in `relevant_doc_ids` appears in the top-5 retrieval results.

## 2. Results

| Metric | Result | Bar | Pass? |
|--------|--------|-----|-------|
| Golden N | _TBD_ | ≥ 40 | |
| Recall@5 | _TBD_ | ≥ 0.60 | |
| TTFT p95 | _TBD_ (ms) | declared | |
| Total latency p95 | _TBD_ (ms) | declared | |

### Latency method

- Hardware / runtime path: _TBD_
- Sample size / query set: _TBD_
- TTFT measurement point: _TBD_ (e.g. first token from stream)
- Total latency: end-to-end until final answer

## 3. Error analysis (required)

List at least five misses: query id, retrieved top ids, why relevant doc missed (chunking, embedding, filter, stale corpus).

## 4. Decision

- [ ] Ship retrieval config for portfolio demo
- [ ] Iterate (what changes next)

**Note:** A demo without this report does not meet CAP 501 acceptance. “Chat with docs on Lambda” without Recall@5 evidence fails.
