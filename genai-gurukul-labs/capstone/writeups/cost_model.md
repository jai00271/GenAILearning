# Cost model — Ops Incident Copilot (template)

**Status:** TEMPLATE — fill assumptions and arithmetic  
**Unit:** USD per 1,000 successful queries (state currency date)

## 1. Assumptions

| Driver | Assumption | Notes |
|--------|------------|-------|
| Avg input tokens / query | _TBD_ | query + retrieved context |
| Avg output tokens / query | _TBD_ | |
| Embedding tokens / query | _TBD_ | or $ / query for managed embed |
| Retrieval infra | _TBD_ | vector DB RU / host share |
| Primary model $ / 1M tokens (in/out) | _TBD_ | |
| Failover model $ / 1M tokens | _TBD_ | usually cheaper/degraded |
| Failover rate | _TBD_% | from prod traces |
| Agent tool loops (avg hops) | _TBD_ | hard cap? |

## 2. Formula (edit to match your stack)

```
cost_per_query =
    embed_cost
  + retrieval_infra_cost
  + primary_llm_cost * (1 - failover_rate)
  + failover_llm_cost * failover_rate
  + tool_overhead

cost_per_1k = 1000 * cost_per_query
```

## 3. Worked example

| Line item | $/query | $/1k |
|-----------|---------|------|
| Embed + retrieve | | |
| Primary LLM | | |
| Failover LLM (expected) | | |
| **Total** | | **_TBD_** |

## 4. Controls that keep the model honest

- Max context tokens; max agent hops; rate limits (`app/rate_limit.py`)
- Cache frequent incident classes
- Kill-switch when daily spend exceeds budget

Without a written model like this, CAP 501 cost criterion fails — a single cloud bill screenshot is not enough.
