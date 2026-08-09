# PROD 404 — Observability & Cost Optimization

Companion lab for `genai-gurukul/modules/prod-404-observability-cost.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest prod-404/tests -q
# GURUKUL_LAB=starter pytest prod-404/tests -q
```

Offline — `TenantCostTracker` (per-tenant attribution) + `CircuitBreaker` /
`run_with_breaker` + `detect_retry_storm`. No live Datadog/Splunk.

Related debug fixture: [`../debug-labs/B-agent-cost-incident/`](../debug-labs/B-agent-cost-incident/)
(soft budget logged only — contrast with the hard circuit breaker here).
