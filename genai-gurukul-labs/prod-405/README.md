# PROD 405 — Deploying GenAI Apps at Scale

Companion lab for `genai-gurukul/modules/prod-405-deploy-scale.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest prod-405/tests -q
# GURUKUL_LAB=starter pytest prod-405/tests -q
```

Offline — `check_latency_budgets` (TTFT vs total) + `plan_tpm` / `plan_tpm_from_mix`
+ `route_with_failover` (multi-provider + mid-stream timeout). No live providers.
