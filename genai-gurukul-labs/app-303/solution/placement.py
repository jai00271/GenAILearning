"""APP 303 — window vs retrieve_later placement heuristic (solution)."""

from __future__ import annotations

from typing import Literal

Placement = Literal["window", "retrieve_later"]

# Kinds that belong in the live context window by default.
_WINDOW_KINDS = frozenset({"live_ticket", "session_goal", "user_pref"})

# Kinds that should stay in a side store and be fetched when needed.
_RETRIEVE_KINDS = frozenset({"runbook", "wiki_page", "pii_note", "audit_log_blob"})


def decide_placement(item: dict) -> Placement:
    """Decide whether an item belongs in the prompt window or retrieve-later.

    Expected keys (others ignored):
      - kind: str — e.g. live_ticket, runbook, pii_note, session_goal, user_pref,
        wiki_page, audit_log_blob
      - sensitivity: optional str — if \"pii\", always retrieve_later

    Decision table (APP 303 lesson):
      live_ticket / session_goal / user_pref → window
      runbook / wiki_page / pii_note / audit_log_blob → retrieve_later
      sensitivity=pii overrides → retrieve_later
    """
    if not isinstance(item, dict):
        raise TypeError("item must be a dict")

    sensitivity = str(item.get("sensitivity", "") or "").lower()
    if sensitivity == "pii":
        return "retrieve_later"

    kind = str(item.get("kind", "") or "").lower().strip()
    if not kind:
        raise ValueError("item.kind is required")

    if kind in _WINDOW_KINDS:
        return "window"
    if kind in _RETRIEVE_KINDS:
        return "retrieve_later"

    raise ValueError(f"unknown kind: {kind!r}")
