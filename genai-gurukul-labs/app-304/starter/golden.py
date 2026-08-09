"""APP 304 — golden JSONL loader + leakage helper (starter)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_WS_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]+")


def normalize_text(text: str) -> str:
    """Lowercase, strip punctuation-ish chars, collapse whitespace.

    Simplification: exact/normalized string match only — not semantic near-dup detection.
    """
    # TODO: implement normalize_text
    raise NotImplementedError


def load_golden_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load a golden evaluation set from JSONL.

    Each non-blank line must be a JSON object with at least:
      - id: str | int
      - question: str
      - relevant_ids: list (doc ids; may be empty)

    Blank lines are skipped. Bad JSON fails fast.
    """
    # TODO: implement load_golden_jsonl
    raise NotImplementedError


def find_leakage(
    train_texts: list[str] | None,
    eval_questions: list[str] | None,
    *,
    normalize: bool = True,
) -> list[dict[str, Any]]:
    """Flag overlaps between train/prompt examples and eval questions.

    Returns a list of hit dicts:
      {"train_index": i, "eval_index": j, "train_text": ..., "eval_question": ...}

    When normalize=True (default), compare normalize_text forms.
    """
    # TODO: implement find_leakage
    raise NotImplementedError


def golden_questions(records: list[dict[str, Any]]) -> list[str]:
    """Convenience: extract question strings from loaded golden records."""
    # TODO: implement golden_questions
    raise NotImplementedError
