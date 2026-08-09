"""
FastAPI skeleton for CAP 501 Ops Incident Copilot.

Prod stubs wired: auth header, rate limit, tracing, failover.
Retrieval/generation are placeholders — replace with your RAG + agent loop.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .auth import require_api_key
from .failover import complete_with_failover, primary_stub, secondary_stub
from .rate_limit import limiter
from .tracing import trace_span

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "corpus" / "fixtures"

app = FastAPI(
    title="Ops Incident Copilot (scaffold)",
    version="501.0.0-scaffold",
    description="CAP 501 scaffold — not a production deploy.",
)


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(5, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    citations: list[dict[str, Any]]
    path: str
    trace_id: str


def _retrieve_stub(query: str, top_k: int) -> list[dict[str, Any]]:
    """Return fixture metadata as fake hits. Replace with real retrieval."""
    hits: list[dict[str, Any]] = []
    for path in sorted(FIXTURES.glob("*")):
        if path.name.startswith(".") or path.suffix.lower() not in {".md", ".json", ".html"}:
            continue
        hits.append(
            {
                "doc_id": path.stem,
                "source_format": path.suffix.lstrip("."),
                "path": str(path.relative_to(ROOT)),
                "score": 0.0,
                "snippet": path.read_text(encoding="utf-8")[:240],
            }
        )
    # Naive: prefer filename token overlap with query
    q = query.lower()
    hits.sort(key=lambda h: sum(tok in h["doc_id"].lower() for tok in q.split()), reverse=True)
    return hits[:top_k]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ops-incident-copilot-scaffold"}


@app.post("/v1/incident/ask", response_model=AskResponse)
def ask_incident(
    body: AskRequest,
    api_key: str = Depends(require_api_key),
) -> AskResponse:
    if not limiter.allow(api_key):
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    with trace_span("incident.ask", {"top_k": body.top_k}) as span:
        citations = _retrieve_stub(body.query, body.top_k)
        prompt = body.query if citations else f"NO_HITS: {body.query}"
        answer, path = complete_with_failover(primary_stub, secondary_stub, prompt)
        span["attributes"]["path"] = path
        span["attributes"]["n_citations"] = len(citations)
        return AskResponse(
            answer=answer,
            citations=citations,
            path=path,
            trace_id=str(span["trace_id"]),
        )
