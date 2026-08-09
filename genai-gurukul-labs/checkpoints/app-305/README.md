# Checkpoint · APP 305 — RAG Deep-Dive

**Known-good** frozen ingest / chunk / retrieve helpers for later modules
(APP 306 vector DBs, capstone). Prefer this package over a learner's
`app-305/starter` unless `GURUKUL_LAB=solution pytest app-305/tests -q` is green
and the team explicitly opts into that code.

## Frozen symbols

| Module | Role |
|---|---|
| `ingest` | metadata, OCR heuristic, fake PDF-table parser, corpus loader |
| `chunk` | `chunk_fixed` · `chunk_structure_aware` |
| `retrieve` | semantic / keyword / hybrid (RRF) + APP 304 metric averages |

Depends on `checkpoints/core-204` (embedder) and `checkpoints/app-304` (P/R@k).

## Version

`__version__ = "305.0.0"`
