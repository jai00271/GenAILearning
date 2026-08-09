"""APP 303 — token-budget conversation memory (solution).

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
    return (
        4
        + count_tokens(message["role"], encoding_name)
        + count_tokens(message["content"], encoding_name)
    )


def total_tokens(messages: list[dict[str, str]], encoding_name: str) -> int:
    return sum(message_tokens(m, encoding_name) for m in messages) + 3


@runtime_checkable
class Summarizer(Protocol):
    def summarize(self, messages: list[dict[str, str]]) -> str:
        """Return a short plain-text summary of the given messages."""
        ...


class FakeSummarizer:
    """Deterministic offline summarizer for pytest — no paid APIs."""

    def summarize(self, messages: list[dict[str, str]]) -> str:
        if not messages:
            return "SUMMARY: (empty)"
        parts: list[str] = []
        for m in messages:
            role = m.get("role", "?")
            content = m.get("content", "")
            snippet = content if len(content) <= 40 else content[:37] + "..."
            parts.append(f"{role}:{snippet}")
        return f"SUMMARY[{len(messages)}]: " + " | ".join(parts)


class ConversationMemory:
    """Append-only chat memory that compacts when over a token budget."""

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
        return total_tokens(self._messages, self.encoding_name) if self._messages else 0

    def append(self, role: str, content: str) -> None:
        if not role:
            raise ValueError("role must be non-empty")
        self._messages.append({"role": role, "content": content})
        self.compact_if_needed()

    def compact_if_needed(self) -> bool:
        """Compact if over budget. Returns True when a compaction ran."""
        if not self._messages:
            return False
        if self.token_count() <= self.token_budget:
            return False

        system: dict[str, str] | None = None
        rest = list(self._messages)
        if rest and rest[0]["role"] == "system":
            system = rest.pop(0)

        if len(rest) <= self.keep_recent:
            # Nothing left to summarize — still over budget.
            raise ValueError("messages exceed token_budget even after keeping only recent turns")

        recent = rest[-self.keep_recent :]
        older = rest[: -self.keep_recent]
        summary_text = self.summarizer.summarize(older)
        summary_msg = {"role": "system", "content": summary_text}

        rebuilt: list[dict[str, str]] = []
        if system is not None:
            rebuilt.append(system)
        rebuilt.append(summary_msg)
        rebuilt.extend(recent)
        self._messages = rebuilt

        if self.token_count() > self.token_budget:
            raise ValueError("messages still exceed token_budget after compaction")
        return True
