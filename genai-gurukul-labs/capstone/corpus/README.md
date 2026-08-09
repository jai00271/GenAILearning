# Corpus stubs — expand toward production scale

These fixtures **represent** a multi-format ops corpus. They are intentionally small.

## Formats (acceptance: ≥3)

| File | Format | Role |
|------|--------|------|
| `fixtures/runbook-auth-crashloop.md` | Markdown | Runbook |
| `fixtures/ticket-inc-1042.json` | JSON | ITSM-style ticket |
| `fixtures/alert-api-5xx.html` | HTML | Observability alert page |

## How to expand (~10k+ chunks narrative)

1. Add one fixture family per service (auth, payments, data plane, observability).
2. Keep provenance fields: `doc_id`, `service`, `source_format`, `updated_at`.
3. Chunk with stable IDs; do not re-chunk without re-labeling golden queries.
4. Mix formats: Markdown runbooks, JSON tickets/exports, HTML alert/dashboard dumps, optional PDF later.
5. Re-run ingestion; freeze new golden labels; re-measure Recall@5 before claiming the eval bar.

Do not claim “production scale” while only these three stubs exist — document your expansion path in the capstone README.
