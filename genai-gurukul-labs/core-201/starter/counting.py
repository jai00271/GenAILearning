"""CORE 201 — token counting with tiktoken (starter)."""

from __future__ import annotations

import tiktoken


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Return the number of tokens for text under the named encoding.

    Use tiktoken.get_encoding(encoding_name). Do not call the network.
    """
    # TODO: load encoding, encode text, return len(ids)
    raise NotImplementedError


def encode_ids(text: str, encoding_name: str = "cl100k_base") -> list[int]:
    """Return the raw token id list (useful for debugging fragmentation)."""
    # TODO
    raise NotImplementedError
