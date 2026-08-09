"""CORE 201 — simplified chat-message token budget (solution)."""

from __future__ import annotations

from counting import count_tokens


def message_tokens(message: dict[str, str], encoding_name: str) -> int:
    role = message["role"]
    content = message["content"]
    return 4 + count_tokens(role, encoding_name) + count_tokens(content, encoding_name)


def total_tokens(messages: list[dict[str, str]], encoding_name: str) -> int:
    return sum(message_tokens(m, encoding_name) for m in messages) + 3


def fit_messages(
    messages: list[dict[str, str]],
    encoding_name: str,
    token_budget: int,
) -> list[dict[str, str]]:
    if not messages:
        return []
    kept = list(messages)
    while total_tokens(kept, encoding_name) > token_budget:
        if len(kept) == 1:
            raise ValueError("last message alone exceeds token_budget")
        kept.pop(0)
    return kept
