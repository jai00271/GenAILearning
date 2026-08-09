# APP 308 — Multi-Agent Systems & Orchestration

Companion lab for `genai-gurukul/modules/app-308-multi-agent.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest app-308/tests -q
# after filling starter TODOs:
# GURUKUL_LAB=starter pytest app-308/tests -q
```

Offline only — pure Python supervisor + worker graph (simulated edges).
No `langgraph` / `crewai` / paid APIs. Shared MCP-shaped tool catalog + trajectory merge.
