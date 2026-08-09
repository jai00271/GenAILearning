"""APP 301 — simple user-typed prompt-injection heuristics (starter).

Teaching tripwire only — not production-grade prevention.
Indirect / RAG-borne injection is out of scope (PROD 403).
"""

from __future__ import annotations

import re

# Implement detect_simple_injection to flag these reason codes when patterns match
# (case-insensitive) in user_text. Return {"flagged": bool, "reasons": list[str]}.
#
# reason codes (stable):
#   - ignore_previous_instructions  e.g. "ignore previous instructions"
#   - disregard_system              e.g. "disregard the system prompt"
#   - reveal_system_prompt          e.g. "reveal your system prompt"
#   - role_hijack                   e.g. "you are now", "act as", "jailbreak", "DAN"
#   - new_instructions_block        e.g. "new instructions:" or "system:"
#
# Empty / whitespace-only input → flagged False, reasons [].


def detect_simple_injection(user_text: str) -> dict[str, object]:
    """Flag common user-typed injection phrases."""
    # TODO
    raise NotImplementedError
