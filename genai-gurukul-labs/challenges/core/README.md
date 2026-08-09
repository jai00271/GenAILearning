# CORE track challenge — Embedding model decision

**Track gate:** after CORE 204 · before APP 301  
**Kind:** open-ended · **no starter/** · **no solution/** · rubric-graded  
**Lesson page:** [`genai-gurukul/modules/core-challenge.html`](../../../genai-gurukul/modules/core-challenge.html)  
**Portfolio language:** English only for the memo and metrics write-up

## Brief

Compare **at least two** embedding models on a small **IT operations / runbook** domain corpus. Report retrieval (or ranking) metrics on the same query set, plus at least one systems metric (latency, throughput, dimension, or estimated cost at a stated document volume). Write a **one-page decision memo in English** that recommends one model for an ops-doc retrieval prototype and states when you would reverse that call.

This is not a RAG build (that is APP 305). It is not a fine-tune. Leaderboard screenshots without domain queries do not count as evaluation evidence.

## Suggested corpus

Theme: IT ops — incident runbooks, on-call notes, service health snippets. Optional fixtures live in [`corpus/`](corpus/) (short `.txt` files). You may extend or replace them; keep the domain coherent and freeze a small labeled query set (roughly 8–15 queries with relevant doc ids is enough at this scale).

Example query shapes:

- “auth pod in CrashLoopBackOff — what should I check first?”
- “TLS certificate expiring in seven days”
- “Kafka consumer lag climbing on payments topic”

## Deliverables

1. **Metrics table** — ≥2 embedding models, same corpus and protocol, stated `k`, at least one quality metric (e.g. Recall@k or MRR) and one systems metric.
2. **One-page decision memo (English)** — ~400–600 words: recommendation, evidence, observed misses, reverse condition (when the other model wins), and any cost / residency / offline constraints.

Submit wherever your portfolio lives (repo folder, Notion, PDF). There is intentionally **no** `starter/` or `solution/` under this challenge.

## Rubric (1–4 each dimension)

**Pass rule:** no dimension below **2**, and average across the four dimensions **≥ 3.0**.

| Dimension | 1 — Inadequate | 2 — Developing | 3 — Solid | 4 — Exemplary |
|---|---|---|---|---|
| **Correctness / artifact** | Deliverables are missing, not in English, or do not compare two real embedding setups on a stated corpus. | A memo and some numbers exist, but the comparison is incomplete, hard to parse, or mixes incompatible setups without disclosure. | A one-page English memo plus a readable metrics table compare ≥2 embedding models on the same domain corpus with clear recommendation. | Artifacts are crisp, reproducible, and would be credible in a design review; tables and memo align without hand-waving. |
| **Evaluation evidence** | Claims rely on vibes, marketing pages, or unrelated leaderboard screenshots with no domain queries. | Some retrieval or similarity numbers appear, but the protocol (queries, relevance, `k`, metric definition) is vague or unreproducible. | A small labeled query set and stated metrics (for example Recall@k or MRR) support the recommendation on this corpus. | Evidence includes honest misses, sensitivity to `k` or preprocessing, and enough detail that a peer could re-run the comparison. |
| **Engineering judgment** | Picks a winner without trade-offs, or optimizes a vanity metric that does not match the retrieval job. | Notes a trade-off superficially but does not connect model choice to the IT-ops retrieval use case. | Weighs quality against practical constraints (dimension, speed, operational fit) and states when the other model wins. | Judgment reads like production triage: clear default, explicit reverse conditions, and scoped next experiments. |
| **Production awareness** | Ignores cost, latency, data residency, dependency risk, or local-vs-cloud implications entirely. | Mentions one production concern in passing without tying it to the recommendation. | Addresses cost and/or latency and at least one operational concern (vendor lock-in, offline/air-gapped needs, or PII in ops text). | Treats embedding choice as a deployable decision: capacity, failure modes, and monitoring or re-evaluation triggers are named. |

## Gate

Score yourself against the rubric before starting the next track (APP 301).
