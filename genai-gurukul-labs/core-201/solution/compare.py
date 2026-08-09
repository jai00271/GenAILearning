"""CORE 201 — compare token footprints across encodings (solution)."""

from __future__ import annotations

from counting import count_tokens


def compare_encodings(text: str, names: list[str]) -> dict[str, int]:
    return {name: count_tokens(text, name) for name in names}
