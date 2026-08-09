"""PROD 403 — PII redaction that can fail on citations (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-403/tests -q
"""

from __future__ import annotations

from typing import Sequence


def redact_pii(text: str) -> str:
    """Redact email / phone / SSN / EID patterns."""
    # TODO
    raise NotImplementedError("TODO: redact_pii")


def contains_pii(text: str) -> bool:
    """True if any teaching PII pattern remains."""
    # TODO
    raise NotImplementedError("TODO: contains_pii")


def redact_answer_with_citations(
    answer: str,
    snippets: Sequence[str],
    *,
    redact_snippets: bool = False,
) -> dict[str, object]:
    """Redact answer; default leaves snippets raw (citation leak demo)."""
    # TODO
    raise NotImplementedError("TODO: redact_answer_with_citations")
