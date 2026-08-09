"""PROD 403 — indirect prompt injection on retrieved chunks (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-403/tests -q
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def detect_indirect_injection(
    chunks: Sequence[str | Mapping[str, Any]],
) -> dict[str, object]:
    """Scan retrieved chunks for document-borne injection cues."""
    # TODO: pattern-scan each chunk; return flagged/hits/reasons (see solution)
    raise NotImplementedError("TODO: detect_indirect_injection")
