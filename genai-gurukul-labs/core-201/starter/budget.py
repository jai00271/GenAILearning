"""CORE 201 — simplified chat-message token budget (starter).

Framing rule (deterministic, teaching-scale — NOT OpenAI's exact bill):
  For each message: overhead = 4 tokens, plus count_tokens(role), plus count_tokens(content).
  Priming overhead for the whole list: +3 tokens (reply priming).

When over budget, drop messages from the front until it fits, but NEVER drop
the last message (assumed to be the latest user turn). If even the last message
alone (plus priming) exceeds the budget, raise ValueError.
"""

from __future__ import annotations

from counting import count_tokens


def message_tokens(message: dict[str, str], encoding_name: str) -> int:
    """Tokens for one {role, content} message under the framing rule above."""
    # TODO
    raise NotImplementedError


def total_tokens(messages: list[dict[str, str]], encoding_name: str) -> int:
    """Sum of per-message tokens + 3 priming tokens."""
    # TODO
    raise NotImplementedError


def fit_messages(
    messages: list[dict[str, str]],
    encoding_name: str,
    token_budget: int,
) -> list[dict[str, str]]:
    """Drop from the front until total_tokens <= budget; keep the last message."""
    # TODO
    raise NotImplementedError
