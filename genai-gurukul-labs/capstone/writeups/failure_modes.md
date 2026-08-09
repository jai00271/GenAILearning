# Failure modes — Ops Incident Copilot (template)

**Status:** TEMPLATE — replace with your observed or staged incidents  
**Required stories:** (1) indirect prompt injection (2) cost blowup

## 1. Indirect prompt injection (retrieved docs)

### Scenario

A ticket work note or runbook paste contains hidden instructions
(`Ignore previous instructions…`, `BEGIN HIDDEN INSTRUCTIONS…`, or tool-exfil wording).
The user query is clean. The retriever places the poisoned chunk in top-k. The model
treats it as trusted policy and attempts a privileged tool call or data exfil.

### Blast radius

- Confused-deputy tool invocation (page storm, secret read, ticket spam)
- Misleading “next steps” that skip safety checks

### Mitigations (map to PROD 403)

- Treat retrieved text as **untrusted data**; never as system policy
- Indirect-injection detectors on chunks before tool planning
- Allowlisted tools + human approval for side-effects
- Citations that do not leak PII from snippets

### Residual risk

Detectors miss paraphrases; humans can still paste poison into tickets. Monitoring and
deny-by-default tools remain mandatory.

### Evidence to attach

- Poison fixture + detector output (pass/fail)
- Trajectory showing halt / refusal

---

## 2. Cost blowup

### Scenario

Unbounded agent loops, repeated retrieval of huge HTML dumps, or primary outage that
fan-outs to an expensive failover model on every token retry → $/query spikes orders of
magnitude above the cost model.

### Blast radius

- Budget exhaustion; rate-limit storms; degraded UX for all tenants

### Mitigations

- Hard max hops / wall-clock per request
- Context size caps; summarize before compose
- Rate limits (`app/rate_limit.py`) and daily spend kill-switch
- Failover to **cheaper degraded** path, not a larger model by default
- Trace attributes for `path`, `n_hops`, `token_in`, `token_out` (`app/tracing.py`)

### Residual risk

New tools bypass hop counters if not registered; cached poison can amplify retries.

### Evidence to attach

- Synthetic FORCE_FAIL / loop demo with caps engaged
- Before/after $/1k from `cost_model.md`

---

## 3. Other modes (optional but strong)

| Mode | Signal | Control |
|------|--------|---------|
| Hallucinated remediation | No citation / wrong doc | Refuse without retrieval hits |
| Stale runbook | `updated_at` old | Freshness filter + warn |
| Auth bypass | Missing `X-API-Key` | `app/auth.py` 401 |

**Acceptance:** both required stories must be written in English with mitigations and residual risk. “We prompted the model to be safe” alone fails.
