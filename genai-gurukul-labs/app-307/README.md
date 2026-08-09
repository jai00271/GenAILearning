# APP 307 — Agents & Tool Use

Companion lab for `genai-gurukul/modules/app-307-agents.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest app-307/tests -q
# after filling starter TODOs:
# GURUKUL_LAB=starter pytest app-307/tests -q
```

Offline only — `FakeLLM` + `ToyMCPClient` (MCP-shaped `tools/list` / `tools/call`).
No paid APIs. LangChain optional in prod; not required here.

Related debug fixture: `debug-labs/B-agent-cost-incident/` (unbounded loop / cost incident).
