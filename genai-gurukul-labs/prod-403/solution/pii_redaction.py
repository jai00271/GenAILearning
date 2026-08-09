"""PROD 403 — PII redaction that can fail on citations/snippets (solution).

Teaching demo: naive redaction of the answer can still leak PII when a citation
or retrieved snippet is appended unredacted.
"""

from __future__ import annotations

import re
from typing import Sequence


_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_EMPLOYEE_ID = re.compile(r"\bEID-\d{4,}\b", re.IGNORECASE)


def redact_pii(text: str) -> str:
    """Redact common PII patterns. Empty/non-string → ValueError for non-str; '' ok."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    out = _EMAIL.sub("[REDACTED_EMAIL]", text)
    out = _PHONE.sub("[REDACTED_PHONE]", out)
    out = _SSN.sub("[REDACTED_SSN]", out)
    out = _EMPLOYEE_ID.sub("[REDACTED_EID]", out)
    return out


def contains_pii(text: str) -> bool:
    """True if any teaching PII pattern remains."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return bool(
        _EMAIL.search(text)
        or _PHONE.search(text)
        or _SSN.search(text)
        or _EMPLOYEE_ID.search(text)
    )


def redact_answer_with_citations(
    answer: str,
    snippets: Sequence[str],
    *,
    redact_snippets: bool = False,
) -> dict[str, object]:
    """Redact the model answer; optionally (fail to) redact citation snippets.

    Default ``redact_snippets=False`` demonstrates the failure mode: answer looks
    clean but citations re-introduce PII. Set True to show the fix.
    """
    if not isinstance(answer, str):
        raise TypeError("answer must be a string")
    snips = list(snippets)
    redacted_answer = redact_pii(answer)
    if redact_snippets:
        citation_block = [redact_pii(s) for s in snips]
    else:
        citation_block = list(snips)

    # Compose a "user-visible" payload the way many RAG UIs do
    composed = redacted_answer
    if citation_block:
        composed = redacted_answer + "\n\nSources:\n" + "\n".join(
            f"- {s}" for s in citation_block
        )

    leak = contains_pii(composed)
    return {
        "redacted_answer": redacted_answer,
        "citations": citation_block,
        "composed": composed,
        "pii_leaked": leak,
        "snippets_redacted": bool(redact_snippets),
        "failure_mode": "citation_reintroduces_pii" if leak and not redact_snippets else None,
    }
