# GenAI System Design — One-pager (English)

Use with your CAP 501 Ops Incident Copilot as the running example.

## Prompt bank (practice aloud)

1. Design an internal **incident copilot** over runbooks + tickets. Where do auth, tenancy, and rate limits live?
2. Compare **RAG vs fine-tuning** for rapidly changing ops docs. What metrics decide?
3. How do you evaluate **retrieval vs answer quality vs agent trajectories** differently?
4. A poisoned ticket note is retrieved. Walk through **indirect injection** defenses and residual risk.
5. Primary LLM region is down. Design **failover** that protects cost and safety.
6. Product wants auto-remediation (`kubectl delete`). How do you say no with a path to yes?
7. Show a **cost model** for 1k queries including tool hops and embedding.
8. Online metrics drift. What offline regression gate blocks deploy (PROD 401 mindset)?

## Answer checklist (every design)

| Checkpoint | Covered? |
|------------|----------|
| Users, trust boundary, data classes | |
| Happy path + degraded path | |
| Eval beat (metric · data · pass-fail) | |
| Latency SLOs (TTFT + total) | |
| Cost controls | |
| Abuse / injection / confused deputy | |
| Observability (traces, token counts) | |
| Explicit non-goals | |

## Sketch template

```
Client → Edge (auth, rate limit, trace)
      → Retriever (multi-format index)
      → Policy (untrusted context, tool allowlist)
      → Generator / Agent (max hops)
      → Failover completer
      → Logs + eval sinks
```
