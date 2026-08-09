# CAP 501 Capstone — Ops Incident Copilot (Option A)

**Course:** GenAI Gurukul · CAP 501  
**Default portfolio build:** Ops Incident Copilot  
**Lesson:** [`genai-gurukul/modules/cap-501-capstone.html`](../../genai-gurukul/modules/cap-501-capstone.html)  
**Language for portfolio artifacts:** English (this README, writeups, eval labels)

This folder is a **scaffold**, not a finished AWS deployment. Structure tests verify the layout. You fill in retrieval, agent behavior, measurements, and evidence against the acceptance table below.

## Portfolio options (context)

| Option | One-line pitch |
|--------|----------------|
| **A · Ops Incident Copilot** (default) | Retrieve runbooks + tickets + alert pages; suggest next-safe on-call steps with citations, halt, and budgets. |
| **B · Ops runbook + ticket copilot** | Ground ITSM tickets in runbook passages; draft triage replies/checklists (not full auto-remediation). |
| **C · ServiceNow-style workflow agent** | Allowlisted workflow transitions + tools with human approval outside side-effects. |

Generic **“chat with your documents on Lambda”** (or equivalent) **fails** acceptance: no golden bar, no cost model, no failure-mode writeup, no prod controls.

## Acceptance criteria (PRD)

Fill the **Your result** column with measured / linked evidence before claiming pass.

| Criterion | Bar (must clear) | Your result |
|-----------|------------------|-------------|
| **Scale / corpus** | Multi-source ops corpus; **≥3 formats** (Markdown runbook, JSON ticket, HTML alert). Fixtures may be small; document how to expand toward ~10k+ chunks / multi-service production scale. | |
| **Latency** | Declare path + hardware. Report **TTFT p95** and **total end-to-end p95** on a frozen query sample (method stated). | |
| **Cost model** | Written **$ / 1k queries** with token, retrieval, and failover-path assumptions. | See `writeups/cost_model.md` |
| **Eval** | Golden set **≥ 40** labeled Q&A; **Recall@5 ≥ 0.60** on frozen labels; protocol (`k`, labeling) stated. | See `eval/` + `writeups/eval_report.md` |
| **Prod features** | Auth header check, tracing, rate limit, failover (secondary path) — stubs wired here; replace with real impl as you harden. | See `app/` |
| **English deliverables** | Eval report; cost model; failure-mode writeup (**indirect injection** + **cost blowup**); README + architecture. | `writeups/` + this file |

## Architecture (scaffold)

```
on-call query
    → FastAPI edge (auth · rate limit · tracing)
    → retrieve (runbook.md · ticket.json · alert.html …)
    → optional agent loop (tools + hard halt)
    → answer + citations
    → on primary failure: failover stub
```

Offline eval uses `eval/golden_set.jsonl`. Cost and failure modes are written evidence, not slides.

```
capstone/
  README.md                 ← you are here
  architecture.md           ← component notes
  requirements.txt          ← optional FastAPI deps for local run
  app/                      ← FastAPI skeleton + prod stubs
  corpus/fixtures/          ← ≥3 format stubs + expand instructions
  eval/                     ← golden ≥40 template
  writeups/                 ← eval · cost · failure modes (English)
  interview/                ← CAP 502 English one-pagers
  tests/                    ← scaffold structure checks only
```

## Local checks

```bash
cd genai-gurukul-labs
pytest capstone/tests -q
```

Optional API smoke (after `pip install -r capstone/requirements.txt`):

```bash
cd capstone
uvicorn app.main:app --reload
# GET /health  ·  POST /v1/incident/ask  with header X-API-Key: dev-key
```

## Expand the corpus (scale narrative)

1. Keep the three formats; add services (auth, payments, data, observability).
2. Chunk consistently; store `doc_id`, `source_format`, `service`, `updated_at`.
3. Target narrative for “production scale”: **~10k+ chunks** across services — fixtures here are intentionally tiny stand-ins.
4. Re-freeze golden labels after major corpus changes; re-run Recall@5.

## Related

- CAP 502 interview materials: [`interview/`](interview/)
- PROD 403 lineage (indirect injection): course module `prod-403-guardrails.html`
