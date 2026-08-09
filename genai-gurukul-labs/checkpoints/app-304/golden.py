"""APP 304 — golden JSONL loader + leakage helper (solution)."""

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
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    lowered = text.lower().strip()
    cleaned = _NON_ALNUM_RE.sub(" ", lowered)
    return _WS_RE.sub(" ", cleaned).strip()


def load_golden_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load a golden evaluation set from JSONL.

    Each non-blank line must be a JSON object with at least:
      - id: str | int
      - question: str
      - relevant_ids: list (doc ids; may be empty)

    Blank lines are skipped. Bad JSON fails fast.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"golden JSONL not found: {p}")
    rows: list[dict[str, Any]] = []
    with p.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON ({exc})") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"line {line_no}: expected a JSON object")
            for key in ("id", "question", "relevant_ids"):
                if key not in obj:
                    raise ValueError(f"line {line_no}: missing required key {key}")
            if not isinstance(obj["question"], str):
                raise ValueError(f"line {line_no}: question must be a string")
            if not isinstance(obj["relevant_ids"], list):
                raise ValueError(f"line {line_no}: relevant_ids must be a list")
            rows.append(obj)
    return rows


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
    if train_texts is None or eval_questions is None:
        raise TypeError("train_texts and eval_questions are required")

    def _key(s: str) -> str:
        return normalize_text(str(s)) if normalize else str(s)

    index: dict[str, list[int]] = {}
    for j, q in enumerate(eval_questions):
        index.setdefault(_key(q), []).append(j)

    hits: list[dict[str, Any]] = []
    for i, t in enumerate(train_texts):
        for j in index.get(_key(t), []):
            hits.append(
                {
                    "train_index": i,
                    "eval_index": j,
                    "train_text": t,
                    "eval_question": eval_questions[j],
                }
            )
    return hits


def golden_questions(records: list[dict[str, Any]]) -> list[str]:
    """Convenience: extract question strings from loaded golden records."""
    return [str(r["question"]) for r in records]
