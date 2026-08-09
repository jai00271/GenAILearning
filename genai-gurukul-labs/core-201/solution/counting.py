"""CORE 201 — token counting with tiktoken (solution)."""

from __future__ import annotations

import tiktoken


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def encode_ids(text: str, encoding_name: str = "cl100k_base") -> list[int]:
    enc = tiktoken.get_encoding(encoding_name)
    return list(enc.encode(text))
