"""FOUND-101 — Pydantic chat schemas (starter)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    """One message in a chat transcript."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str = Field(min_length=1)
    name: str | None = None


def parse_turns(payloads: list[dict[str, Any]]) -> list[ChatTurn]:
    """Validate a list of dicts into ChatTurn models (fail fast on bad rows)."""
    raise NotImplementedError("Implement parse_turns")
