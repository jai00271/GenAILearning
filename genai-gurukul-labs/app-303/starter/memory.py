"""APP 303 — token-budget conversation memory (starter).

CORE 201 framing (teaching-scale, deterministic):
  per message: 4 + count_tokens(role) + count_tokens(content)
  list priming: +3

When over budget: keep optional leading system message, summarize the
compressible middle via an injectable Summarizer, keep the last
`keep_recent` messages verbatim.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import tiktoken


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def message_tokens(message: dict[str, str], encoding_name: str) -> int:
    """Tokens for one {role, content} message under CORE 201 framing."""
    # TODO
    raise NotImplementedError


def total_tokens(messages: list[dict[str, str]], encoding_name: str) -> int:
    """Sum of per-message tokens + 3 priming tokens."""
    # TODO
    raise NotImplementedError


@runtime_checkable
class Summarizer(Protocol):
    def summarize(self, messages: list[dict[str, str]]) -> str:
        """Return a short plain-text summary of the given messages."""
        ...


class FakeSummarizer:
    """Deterministic offline summarizer for pytest — no paid APIs.

    Spec (match solution):
      SUMMARY[<n>]: role:snippet | role:snippet | ...
      where snippet is content truncated to 40 chars with '...' if longer.
      Empty list → 'SUMMARY: (empty)'
    """

    def summarize(self, messages: list[dict[str, str]]) -> str:
        # TODO
        raise NotImplementedError


class ConversationMemory:
    """Append-only chat memory that compacts when over a token budget.

    Spec:
      - append(role, content) adds a message then calls compact_if_needed()
      - compact_if_needed(): if token_count() > budget:
          * peel leading system message (if any) and preserve it
          * keep last keep_recent messages verbatim
          * summarize the middle with self.summarizer → one system SUMMARY msg
          * rebuild: [system?] + [summary] + recent
          * if still over budget (or nothing to summarize), raise ValueError
        Returns True iff compaction ran.
    """

    def __init__(
        self,
        token_budget: int,
        encoding_name: str = "cl100k_base",
        summarizer: Summarizer | None = None,
        keep_recent: int = 2,
    ) -> None:
        if token_budget < 1:
            raise ValueError("token_budget must be >= 1")
        if keep_recent < 1:
            raise ValueError("keep_recent must be >= 1")
        self.token_budget = token_budget
        self.encoding_name = encoding_name
        self.summarizer: Summarizer = summarizer or FakeSummarizer()
        self.keep_recent = keep_recent
        self._messages: list[dict[str, str]] = []

    def messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def token_count(self) -> int:
        # TODO: 0 if empty, else total_tokens(...)
        raise NotImplementedError

    def append(self, role: str, content: str) -> None:
        # TODO
        raise NotImplementedError

    def compact_if_needed(self) -> bool:
        # TODO
        raise NotImplementedError
