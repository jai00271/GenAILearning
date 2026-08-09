# GenAI Interview Question Bank (English)

Short prompts for GenAI engineer / applied scientist / ML platform roles. Prefer answers that cite **your** CAP 501 numbers.

## Retrieval & RAG

- How do you choose chunk size for mixed Markdown / JSON / HTML ops corpora?
- Define Recall@5 vs MRR; when is each the better gate?
- Hybrid search: what fails if you only use dense embeddings on ticket IDs?

## Agents & tools

- When is a single agent enough? When does a second agent pay for itself?
- How do you log trajectories so PROD-style judges can score them?
- Hard halt conditions you would refuse to ship without?

## Evaluation & production

- Offline golden vs online shadow — order of operations?
- LLM-as-judge disagrees with humans — ship or not?
- What regression `max_drop` means for your Recall@5 gate?

## Safety & cost

- Indirect vs direct prompt injection — example from tickets/runbooks.
- How does rate limiting interact with agent retries?
- Show mental math for $/1k when failover_rate doubles.

## Behavioral / portfolio

- Walk me through a miss in your golden set and what you changed.
- What did you deliberately not build in the capstone, and why?
- How would you staff on-call for this copilot itself?

## Red flags (avoid)

- No labeled eval; only screenshots.
- Unbounded tools in production demos.
- “Chat with docs on Lambda” as the entire design.
