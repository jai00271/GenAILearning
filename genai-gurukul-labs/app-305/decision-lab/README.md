# APP 305 — Decision lab: ingestion & chunking under constraints

**Kind:** decision · portfolio memo in **English** · no hidden solution key  
**Lesson:** [`genai-gurukul/modules/app-305-rag.html`](../../../genai-gurukul/modules/app-305-rag.html)  
**Convergent code lab (separate):** `../` starter/solution/tests

## Scenario constraints (given)

You are proposing the **document ingestion + chunking** strategy for an internal
IT/HR assistant that answers from mixed enterprise files:

1. **Latency:** p95 end-to-end answer ≤ **1.8s** on CPU-only retrieval (embed +
   search + prompt pack). Heavy OCR on every query is out of budget.
2. **Cost:** embedding + re-embed budget ≤ **$40/month** at ~2k docs with ~15%
   monthly churn. Prefer incremental ingest; avoid re-embedding the whole corpus
   weekly.
3. **Corpus messiness:** ~40% clean Markdown runbooks, ~35% PDF exports with
   **tables** (leave matrices, entitlement grids), ~25% **scanned** PDFs with
   noisy OCR. Tables must remain answerable (e.g. “MaxDays for Sick leave”).
4. **Security / trust:** OCR pages have historically contained stale secrets and
   wrong instructions; quarantining low-trust text matters more than squeezing
   one more Recall point.

LlamaIndex (or similar framework) is **allowed as one option**, but you must
compare it to a **raw pipeline** (parse → chunk → embed → hybrid retrieve) and
say what you would own vs. delegate.

## Deliverable

Write a **one-page English memo** (~400–700 words) that:

- Chooses a concrete **ingestion** path (parsers, OCR policy, metadata) and a
  **chunking** strategy (fixed vs structure-aware / table-aware, sizes).
- Defends the choice against the four rubric dimensions below.
- States **metric / data / pass-fail** using APP 304 vocabulary (e.g. Recall@5
  on a labeled leave-table + runbook golden; ship only if Recall@5 ≥ X and
  p95 ≤ 1.8s).
- Names at least one **failure mode** you accept and one you refuse.

Submit in your portfolio (repo doc, Notion, or PDF). There is no `solution/`
answer key for this decision lab.

## Rubric (1–4 each dimension)

**Pass rule:** no dimension below **2**, and average across the four dimensions
**≥ 3.0**.

| Dimension | 1 — Inadequate | 2 — Developing | 3 — Solid | 4 — Exemplary |
|---|---|---|---|---|
| **Correctness / artifact** | The memo is missing, not in English, or never states a concrete ingestion and chunking choice. | A memo exists but the chosen strategy is vague, internally contradictory, or omits either ingestion or chunking. | A one-page English memo names a clear ingestion path and chunking strategy that fit the written constraints. | The artifact would survive a design review: reproducible choices, explicit defaults, and aligned appendix. |
| **Constraint fit** | Ignores latency, cost, or corpus messiness, or optimizes a vanity setup that violates the given budgets. | Mentions constraints but does not connect them to the chosen parsers, OCR policy, or chunk sizes. | Ties the recommendation to latency, cost/churn, and messy tables/OCR with explicit trade-offs. | Shows reverse conditions (when you would switch strategies) if latency, cost, or messiness ratios change. |
| **Evaluation evidence** | Relies on vibes or vendor marketing with no APP 304-style metric/data/pass-fail. | Names a metric but leaves the dataset, `k`, or ship gate unspecified. | Declares metric, golden/data slice, and pass-fail gate (for example Recall@k plus a latency ceiling). | Evidence plan includes an honest failure slice (tables or OCR) and how you would re-measure after parser changes. |
| **Production / trust awareness** | Ignores OCR quarantine, secret leakage in scanned pages, parser failure modes, or operational ownership. | Mentions one production concern in passing without changing the design. | Addresses trust (quarantine/low-trust chunks), parser failures, and who owns framework vs raw pipeline pieces. | Treats ingestion as a deployable system: monitoring hooks, re-embed triggers, and security citations or policies are named. |
