# PROD track challenge — CI gate + flag/canary + risk memo

**Track gate:** after PROD 406 · before CAP 501  
**Kind:** open-ended · **no starter/** · **no solution/** · rubric-graded  
**Lesson page:** [`genai-gurukul/modules/prod-challenge.html`](../../../genai-gurukul/modules/prod-challenge.html)  
**Portfolio language:** English only for the memo and gate/canary write-up

## Brief

Design a **CI eval gate** and a **feature-flag / canary plan** for a prompt or model change in a production GenAI slice (RAG and/or tool-using agent). Write a **one-page English memo** that covers **both**:

1. **Indirect prompt injection** — retrieved documents / external content as the attack surface (PROD 403); controls and residual risk.
2. **Cost blowup** — unbounded tool loops, soft-only budgets, retry storms, missing tenant attribution (PROD 404 / Debug Lab B); hard ceilings and monitoring.

This is not CAP 501. It is not a fine-tune. Screenshots without thresholds do not count as evaluation evidence.

## Suggested constraints

- Name a concrete system slice (e.g. IT-ops RAG agent with a small tool allowlist).
- Offline quality metrics + ≥1 trace/cost signal (tool error rate, usd/tenant, retry rate, p95).
- Fail closed when offline scores look flat but traces worsen.
- Sticky percentage canary (1→5→25→100 or defend your stages); rollback = previous prompt/model artifact.
- Study aids: `prod-403`–`prod-406` labs and `debug-labs/B-agent-cost-incident/` — do not submit those folders as the challenge artifact.

## Deliverables

1. **CI gate design** — metrics, baselines, thresholds (`max_drop` / worsen), fail-closed annotation text.
2. **Flag / canary plan** — sticky key, percentage stages, per-stage watchlist, rollback triggers.
3. **One-page English memo (~400–600 words)** — injection + cost blowup, how gate/canary catch regressions, reverse conditions.

Submit wherever your portfolio lives. There is intentionally **no** `starter/` or `solution/` under this challenge.

## Rubric (1–4 each dimension)

**Pass rule:** no dimension below **2**, and average across the four dimensions **≥ 3.0**.

| Dimension | 1 — Inadequate | 2 — Developing | 3 — Solid | 4 — Exemplary |
|---|---|---|---|---|
| **Correctness / artifact** | Deliverables are missing, not in English, or omit the CI gate, canary/flag plan, or memo. | Artifacts exist but are vague, incomplete, or contradict each other on thresholds or stages. | A clear CI gate, staged flag/canary plan, and one-page English memo align on a coherent ship path. | Artifacts are review-ready: concrete thresholds, sticky canary stages, rollback triggers, and memo that a staff eng would accept. |
| **Evaluation evidence** | No named metrics, thresholds, or fail rules; vibes-only ship criteria. | Some metrics named, but pass/fail rules, baseline freeze, or trace worsen handling are fuzzy. | Offline quality metrics plus at least one trace/cost signal with explicit thresholds and fail-closed behavior. | Evidence includes how flat-eval/worse-trace cases fail the gate and what would be re-measured after rollback. |
| **Engineering judgment** | Big-bang cutover or flag-free deploy; ignores progressive delivery. | Mentions canary superficially without sticky keys, stages, or rollback. | Weighs staged rollout vs risk; sticky percentage plan with watchlist and rollback conditions. | Judgment reads like production triage: default canary, explicit freeze/rollback, scoped next experiments. |
| **Production awareness** | Ignores indirect injection or cost blowup entirely. | Mentions one risk in passing without controls or residual risk. | Addresses both indirect injection and cost blowup with controls tied to gate/canary monitoring. | Treats both as deployable risks: detection signals, hard ceilings, tenant attribution, and residual risk named. |

## Gate

Score yourself against the rubric before starting the next track (CAP 501).
