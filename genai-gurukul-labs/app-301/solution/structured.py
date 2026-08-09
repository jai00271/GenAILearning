"""APP 301 — ask for JSON and validate with Pydantic (solution).

Portable pattern: instruct JSON in the prompt → completer → extract → validate.
Provider JSON-mode / schema-constrained decoding is an APP 302 topic.
"""

from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from completer import Completer

T = TypeVar("T", bound=BaseModel)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_json_object(text: str) -> dict[str, Any]:
    """Pull the first JSON object from model text (raw or fenced).

    Strategy:
      1) Prefer content inside the first ``` / ```json fence if present.
      2) Otherwise use the full text.
      3) Locate the first '{' and parse with json.JSONDecoder.raw_decode.
      4) Require the top-level value to be a dict.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")

    candidate = text.strip()
    fence = _FENCE_RE.search(candidate)
    if fence:
        candidate = fence.group(1).strip()

    start = candidate.find("{")
    if start < 0:
        raise ValueError("no JSON object found in model output")

    decoder = json.JSONDecoder()
    try:
        obj, _end = decoder.raw_decode(candidate[start:])
    except json.JSONDecodeError as exc:
        raise ValueError(f"failed to parse JSON object: {exc}") from exc

    if not isinstance(obj, dict):
        raise ValueError("top-level JSON value must be an object")
    return obj


def ask_structured(
    completer: Completer,
    messages: list[dict[str, str]],
    schema: type[T],
    *,
    model: str | None = None,
) -> T:
    """Call completer, extract a JSON object, validate into ``schema``.

    Raises ValueError on extract failure; pydantic.ValidationError on schema mismatch.
    """
    if not messages:
        raise ValueError("messages must be non-empty")
    raw = completer.complete(messages, model=model)
    data = extract_json_object(raw)
    return schema.model_validate(data)


# Re-export for callers that want the exception type nearby.
__all__ = ["ask_structured", "extract_json_object", "ValidationError"]
