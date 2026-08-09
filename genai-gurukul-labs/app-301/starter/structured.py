"""APP 301 — ask for JSON and validate with Pydantic (starter).

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
    # TODO
    raise NotImplementedError


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
    # TODO
    raise NotImplementedError


__all__ = ["ask_structured", "extract_json_object", "ValidationError"]
