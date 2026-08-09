"""PROD 403 — indirect prompt injection on retrieved chunks (solution).

Teaching tripwire for RAG-borne / document-borne injection (OWASP LLM01 indirect).
Not a production-grade filter.
"""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence


# Patterns aimed at instructions embedded in *documents* (not only user chat).
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "ignore_previous_instructions",
        re.compile(
            r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
            re.IGNORECASE,
        ),
    ),
    (
        "system_override",
        re.compile(
            r"(system\s*prompt\s*:|new\s+system\s+instructions?\s*:|"
            r"override\s+(the\s+)?(system|developer)\s+(prompt|instructions?))",
            re.IGNORECASE,
        ),
    ),
    (
        "tool_exfil",
        re.compile(
            r"(call\s+the\s+\w+\s+tool|exfiltrat\w*|send\s+(secrets?|api\s*keys?)\s+to|"
            r"include\s+the\s+system\s+prompt)",
            re.IGNORECASE,
        ),
    ),
    (
        "hidden_instruction_markers",
        re.compile(
            r"(BEGIN\s+HIDDEN\s+INSTRUCTIONS?|<\s*!--\s*prompt|"
            r"\[INST\]|<<SYS>>)",
            re.IGNORECASE,
        ),
    ),
    (
        "assistant_roleplay_hijack",
        re.compile(
            r"(you\s+are\s+now\s+|disregard\s+safety|jailbreak|"
            r"do\s+not\s+follow\s+the\s+user)",
            re.IGNORECASE,
        ),
    ),
    (
        "confused_deputy_tool",
        re.compile(
            r"(always\s+call\s+\w+\s+with|tool\s*:\s*\w+\s+must|"
            r"when\s+retrieved,?\s+invoke)",
            re.IGNORECASE,
        ),
    ),
]


def _chunk_text(chunk: str | Mapping[str, Any]) -> tuple[str, str]:
    """Return (id, text) from a raw string or {id,text}/{doc_id,content} map."""
    if isinstance(chunk, str):
        return ("", chunk)
    if not isinstance(chunk, Mapping):
        raise TypeError("chunk must be str or mapping")
    cid = str(chunk.get("id") or chunk.get("doc_id") or chunk.get("chunk_id") or "")
    text = chunk.get("text")
    if text is None:
        text = chunk.get("content")
    if text is None:
        text = chunk.get("body")
    if not isinstance(text, str):
        raise TypeError("chunk mapping must include string text/content")
    return cid, text


def detect_indirect_injection(
    chunks: Sequence[str | Mapping[str, Any]],
) -> dict[str, object]:
    """Scan retrieved chunks for document-borne injection cues.

    Returns
    -------
    ``{"flagged": bool, "hits": [{"index", "id", "reasons", "snippet"}],
      "reasons": [...unique...]}``
    """
    if not isinstance(chunks, Sequence) or isinstance(chunks, (str, bytes)):
        raise TypeError("chunks must be a sequence of strings or mappings")

    hits: list[dict[str, object]] = []
    all_reasons: list[str] = []
    seen_reasons: set[str] = set()

    for i, chunk in enumerate(chunks):
        cid, text = _chunk_text(chunk)
        if not text or not text.strip():
            continue
        reasons: list[str] = []
        for code, pattern in _PATTERNS:
            if pattern.search(text):
                reasons.append(code)
                if code not in seen_reasons:
                    all_reasons.append(code)
                    seen_reasons.add(code)
        if reasons:
            snippet = text.strip().replace("\n", " ")
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            hits.append(
                {
                    "index": i,
                    "id": cid,
                    "reasons": reasons,
                    "snippet": snippet,
                }
            )

    return {
        "flagged": bool(hits),
        "hits": hits,
        "reasons": all_reasons,
        "n_chunks": len(chunks),
        "n_flagged": len(hits),
    }
