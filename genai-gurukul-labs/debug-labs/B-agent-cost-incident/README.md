# Debug Lab B — Agent Cost Incident

**Module link:** APP 307 · [`app-307-agents.html`](../../../genai-gurukul/modules/app-307-agents.html)  
**Deepen in:** PROD 404 · Observability & Cost Optimization  
**Kind:** debug fixture · **no TODO markers** · **no adjacent solution**

This folder ships a ReAct-shaped agent that **runs cleanly** and still **burns past a soft USD budget** by never treating the budget as a hard stop. Your job is root-cause analysis, not filling stubs.

## Run

```bash
cd genai-gurukul-labs
source .venv/bin/activate
python debug-labs/B-agent-cost-incident/unbounded_agent.py
```

Expected: the script prints a high step count, `budget_exceeded=True`, many `budget_warning` events, and writes `incident_report.json`. There is no early halt at the soft budget.

## RCA checklist (short)

1. Diff **stop conditions** — where is `max_steps` / kill-switch? Is the soft budget enforced or only logged?
2. Diff **tool loop** — does the model stub ever emit a final answer without `tool_calls`?
3. Diff **meters** — which events increment USD? LLM turns vs tool surcharges.
4. Write a 5–10 line English note: *defect → evidence → fix hypothesis* (e.g. hard halt on budget, circuit breaker, idempotent tools).
5. Optional: patch locally; do **not** expect a `solution/` folder here.

Compare with the convergent APP 307 lab (`run_react(..., max_steps=...)`) where the circuit breaker is real.

Withheld: intentional defects are not labeled as bugs in code comments beyond the incident framing. Discover them with the checklist.
