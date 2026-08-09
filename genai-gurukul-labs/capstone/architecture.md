# Architecture — Ops Incident Copilot (scaffold)

## Components

| Piece | Path | Role |
|-------|------|------|
| API edge | `app/main.py` | FastAPI routes; composes stubs |
| Auth | `app/auth.py` | Require `X-API-Key` (stub) |
| Rate limit | `app/rate_limit.py` | In-memory token bucket stub |
| Tracing | `app/tracing.py` | Request-span dict stub (swap for OTel) |
| Failover | `app/failover.py` | Secondary completer when primary raises |
| Corpus | `corpus/fixtures/` | md / json / html stubs |
| Eval | `eval/golden_set.jsonl` | ≥40 Q&A placeholders |
| Writeups | `writeups/` | English portfolio evidence |

## Request path

1. Client sends `POST /v1/incident/ask` with `X-API-Key`.
2. Rate limiter admits or rejects.
3. Tracer opens a span (`request_id`).
4. Retriever stub returns fixture hits (replace with real RAG).
5. Primary completer stub drafts answer; on failure, failover stub runs.
6. Response includes `citations`, `trace_id`, and `path` (`primary` | `failover`).

## Non-goals (scaffold)

- No real AWS/Lambda deploy in tests.
- No live LLM required for structure pytest.
- No claim of Recall@5 until you measure on frozen labels.
