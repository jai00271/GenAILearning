"""APP 301 — simple user-typed prompt-injection heuristics (solution).

Teaching tripwire only — not production-grade prevention.
Indirect / RAG-borne injection is out of scope (PROD 403).
"""

from __future__ import annotations

import re

# (reason_code, compiled pattern) — matched case-insensitively against user text.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "ignore_previous_instructions",
        re.compile(
            r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
            re.IGNORECASE,
        ),
    ),
    (
        "disregard_system",
        re.compile(
            r"(disregard|override|bypass)\s+(the\s+)?(system\s+)?(prompt|instructions?|rules?)",
            re.IGNORECASE,
        ),
    ),
    (
        "reveal_system_prompt",
        re.compile(
            r"(reveal|show|print|dump|repeat)\s+(me\s+)?(your\s+)?(system\s+prompt|hidden\s+instructions?)",
            re.IGNORECASE,
        ),
    ),
    (
        "role_hijack",
        re.compile(
            r"\b(you\s+are\s+now|act\s+as|pretend\s+to\s+be|jailbreak|DAN\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "new_instructions_block",
        re.compile(
            r"(new\s+instructions?\s*:|system\s*:\s*)",
            re.IGNORECASE,
        ),
    ),
]


def detect_simple_injection(user_text: str) -> dict[str, object]:
    """Flag common user-typed injection phrases.

    Returns ``{"flagged": bool, "reasons": list[str]}``.
    Empty / non-string input → not flagged (no reasons).
    Reasons are stable reason codes (unique, insertion order).
    """
    if not isinstance(user_text, str) or not user_text.strip():
        return {"flagged": False, "reasons": []}

    reasons: list[str] = []
    seen: set[str] = set()
    for code, pattern in _PATTERNS:
        if pattern.search(user_text) and code not in seen:
            reasons.append(code)
            seen.add(code)

    return {"flagged": bool(reasons), "reasons": reasons}
