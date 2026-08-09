# PROD 402 — Decision lab: prompt vs RAG vs fine-tune

**Kind:** decision · portfolio memo in **English** · no hidden solution key  
**Lesson:** [`genai-gurukul/modules/prod-402-fine-tuning.html`](../../../genai-gurukul/modules/prod-402-fine-tuning.html)  
**Convergent code lab (separate):** `../` starter/solution/tests (`recommend_adaptation`, toy LoRA)

## Scenario constraints (given)

You own an internal IT assistant (leave policy + VPN runbooks). Leadership wants
to “just fine-tune” after a flashy demo. You have:

1. **Eval evidence (offline golden, n=120):** prompting 0.71, RAG 0.78, LoRA-FT 0.81
   on the **demo slice** the vendor showed — but on the **held-out golden** the same
   LoRA run scores **0.64** (prompting 0.70, RAG 0.77).
2. **Knowledge churn:** entitlement tables change monthly; VPN runbooks weekly.
3. **Data risk:** the FT train file was scraped from the same ticket dump that seeded
   30% of golden items (leakage suspected, not proven).
4. **Budget:** one [PAID] SageMaker Training Job is on the table (~check current AWS
   pricing as of August 2026; treat as optional). Local LoRA on a tiny model is
   allowed as a fallback experiment; huge downloads are out of scope for this course.

## Deliverable

Write a **one-page English memo** (~400–700 words) that:

- Chooses **prompting**, **RAG**, or **fine-tune (PEFT/LoRA)** as the *next*
  production move (you may sequence them).
- Defends the choice with the eval numbers above (demo vs golden).
- Names leakage + catastrophic forgetting risks and what you would measure next.
- States a ship gate in PROD 401 vocabulary (metric / data / pass-fail), including a
  regression max-drop vs the current RAG baseline.

Submit in your portfolio. There is no `solution/` answer key for this decision lab.

## Rubric (1–4 each dimension)

**Pass rule:** no dimension below **2**, and average across the four dimensions
**≥ 3.0**.

| Dimension | 1 — Inadequate | 2 — Developing | 3 — Solid | 4 — Exemplary |
|---|---|---|---|---|
| **Correctness / artifact** | Missing, not English, or never names prompting/RAG/FT. | Names a choice but contradicts itself or ignores demo vs golden. | Clear one-page choice with a coherent next step. | Review-ready: sequencing, defaults, and explicit non-goals. |
| **Eval evidence** | Vibes / vendor demo only. | Mentions scores but not demo/golden gap. | Uses the given numbers; treats golden as the ship signal. | Adds what extra slice you would label before FT. |
| **Risk awareness** | Ignores leakage and forgetting. | Name-drops risks without changing the decision. | Ties leakage/forgetting/churn to the recommendation. | Specifies measurements + kill criteria (e.g. max golden drop). |
| **Production judgment** | “Always fine-tune” or “never fine-tune” dogma. | Mentions cost/ops once. | Connects to regression gate + ownership of eval harness. | States when you *would* revisit FT (clean splits, stable facts, golden win). |
