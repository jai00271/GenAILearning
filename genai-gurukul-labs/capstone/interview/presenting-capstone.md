# Presenting the Capstone (English one-pager)

**Audience:** GenAI / ML platform / applied AI interviews  
**Artifact set:** CAP 501 README acceptance table + `writeups/`  

## 3-minute spine (do not reorder)

1. **Problem** — On-call needs next-safe steps grounded in runbooks, tickets, and alerts.
2. **Eval** — Golden ≥40; Recall@5 ≥ 0.60; state labeling unit and freeze.
3. **Latency** — TTFT p95 and total p95 on a named path.
4. **Cost** — $ / 1k queries with failover assumptions.
5. **Failure modes** — Indirect injection via retrieved docs; cost blowup from unbounded loops.
6. **System sketch** — Auth, rate limit, tracing, failover at the edge; RAG (+ optional agent) behind.
7. **Judgment** — What you postponed (full auto-remediation, multi-agent crew) and reverse triggers.

## Phrases that work

- “Retrieval quality is gated by Recall@5 on a frozen labeled set — here is the miss analysis.”
- “Failover is a degraded path with a cheaper model, not a silent retry storm.”
- “Retrieved text is untrusted data; tools are allowlisted.”

## Phrases that fail

- “We put the docs on Lambda / a Bedrock KB and users chat with them.”
- “The model is usually right” with no golden protocol.
- “Safety is in the system prompt” with no residual risk.

## Leave-behind links

- `capstone/README.md` (acceptance table filled)
- `writeups/eval_report.md`, `cost_model.md`, `failure_modes.md`
- `architecture.md`
