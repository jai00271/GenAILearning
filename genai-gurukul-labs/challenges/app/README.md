# APP track challenge — RAG + single-agent slice

**Track gate:** after APP 308 · before PROD 401  
**Kind:** open-ended · **no starter/** · **no solution/** · rubric-graded  
**Lesson page:** [`genai-gurukul/modules/app-challenge.html`](../../../genai-gurukul/modules/app-challenge.html)  
**Portfolio language:** English only for the memo and metrics write-up

## Brief

Design a **small RAG + single-agent** slice under explicit constraints. Retrieval is a tool; one agent loop may call it (plus at most a tiny auxiliary tool set). **Do not** default to multi-agent orchestration — APP 308 taught the tax; prove the single-agent slice first.

Report **APP 304-style metrics** on a frozen query set (e.g. Recall@k, MRR, or P@k — defend your choice) plus at least one systems metric (latency, mean hops, or tool-error rate). Write a **one-page English trade-off memo** that states what you shipped, what you postponed, and when you would reverse (second agent, different vector store, wider catalog, etc.).

This is not the CAP 501 capstone. It is not a fine-tune. Demo GIFs without metrics do not count as evaluation evidence.

## Suggested constraints

- Domain: short IT operations / runbook docs (optional fixtures: [`../core/corpus/`](../core/corpus/)).
- Local-first embedder / Ollama where possible; label any paid API.
- Max tools: retrieval + ≤2 auxiliaries.
- Hard halt: max agent steps / graph hops.
- If you use LangChain / LangGraph / LlamaIndex / CrewAI, name the seams you still own (tool catalog, trajectory log, eval gates).

## Deliverables

1. **Metrics table** — APP 304-style quality metric(s) on a stated query set + ≥1 systems metric.
2. **One-page trade-off memo (English)** — ~400–600 words: design, constraints, why single-agent, reverse conditions, lock-in/operational notes.
3. **Optional:** a short trajectory sample (scripted/FakeLLM OK) showing tool use + halt.

Submit wherever your portfolio lives. There is intentionally **no** `starter/` or `solution/` under this challenge.

## Rubric (1–4 each dimension)

**Pass rule:** no dimension below **2**, and average across the four dimensions **≥ 3.0**.

| Dimension | 1 — Inadequate | 2 — Developing | 3 — Solid | 4 — Exemplary |
|---|---|---|---|---|
| **Correctness / artifact** | Deliverables are missing, not in English, or do not describe a real RAG + single-agent slice under stated constraints. | A memo and some design notes exist, but the slice is vague, incomplete, or mixes incompatible setups without disclosure. | A one-page English memo plus a readable metrics table describe a constrained RAG tool + single-agent design with a clear recommendation. | Artifacts are crisp, reproducible, and would be credible in a design review; tables, trajectory notes, and memo align. |
| **Evaluation evidence** | Claims rely on vibes, screenshots, or demos with no APP 304-style metrics on a stated query set. | Some numbers appear, but the protocol (queries, relevance, `k`, metric definition) is vague or unreproducible. | A small labeled query set and stated APP 304-style metrics (for example Recall@k or MRR) plus one systems metric support the write-up. | Evidence includes honest misses, trajectory or hop observations, and enough detail that a peer could re-run the comparison. |
| **Engineering judgment** | Defaults to multi-agent or a heavy framework without trade-offs, or ignores the single-agent constraint. | Notes a trade-off superficially but does not connect choices to constraints and the retrieval+agent job. | Weighs single-agent vs multi-agent, tool-catalog scope, and storage/retrieval choices; states when the call reverses. | Judgment reads like production triage: clear default, explicit reverse conditions, scoped next experiments. |
| **Production awareness** | Ignores cost, latency, halt conditions, data residency, or dependency/lock-in risk entirely. | Mentions one production concern in passing without tying it to the recommendation. | Addresses latency and/or cost and at least one operational concern (halt/max-steps, tool allowlists, vendor lock-in, or local-first needs). | Treats the slice as deployable: failure modes, monitoring or re-eval triggers, and framework-seam ownership are named. |

## Gate

Score yourself against the rubric before starting the next track (PROD 401).
