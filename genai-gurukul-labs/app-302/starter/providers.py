"""APP 302 — LLM client interface, Ollama (httpx), cloud stubs, cost + quantization helpers.

Starter: fill in the TODOs. Tests import via GURUKUL_LAB=starter|solution.

Cloud SDKs (openai / anthropic / boto3) are NOT required — stubs keep CI green.
Default live path is Ollama over httpx when a server is running.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from typing import Any, Protocol, runtime_checkable

import httpx

Message = dict[str, str]


@runtime_checkable
class LLMClient(Protocol):
    """Provider-agnostic thin interface used by APP labs."""

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        """Return the full assistant text for a chat turn list."""
        ...

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        """Yield text deltas (tokens or chunks) until the completion finishes."""
        ...


def _require_messages(messages: Sequence[Message]) -> list[Message]:
    if not messages:
        raise ValueError("messages must be non-empty")
    out: list[Message] = []
    for m in messages:
        if "role" not in m or "content" not in m:
            raise ValueError("each message needs role and content")
        out.append({"role": str(m["role"]), "content": str(m["content"])})
    return out


class OllamaClient:
    """Real HTTP client for Ollama `/api/chat` (httpx).

    Spec:
    - POST {base_url}/api/chat with JSON {model, messages, stream}
    - complete: stream=False → return body["message"]["content"]
    - stream_tokens: stream=True → iterate NDJSON lines; yield message.content
      pieces; stop when event["done"] is true
    - Reject empty messages via _require_messages
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://127.0.0.1:11434",
        client: httpx.Client | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OllamaClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        # TODO: POST /api/chat stream=False; return assistant content
        raise NotImplementedError

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        # TODO: POST /api/chat stream=True; yield content deltas until done
        raise NotImplementedError
        yield  # pragma: no cover — makes this a generator for type checkers


class StubOpenAIClient:
    """Deterministic OpenAI-shaped stub — no network, no API key.

    complete → "[openai:{model}] {last_user_content}"
    stream_tokens → words of that string, each followed by a space
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        # TODO
        raise NotImplementedError

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        # TODO
        raise NotImplementedError
        yield  # pragma: no cover


class StubAnthropicClient:
    """Deterministic Anthropic Messages-shaped stub — no network.

    complete → "[anthropic:{model}] {last_user_content}"
    stream_tokens → yield 8-character slices of that string
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        self.model = model

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        # TODO
        raise NotImplementedError

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        # TODO
        raise NotImplementedError
        yield  # pragma: no cover


class StubBedrockClient:
    """Deterministic Bedrock Converse-shaped stub — no AWS creds.

    complete → "[bedrock:{model_id}] {last_user_content}"
    stream_tokens → single yield of complete()
    Accept model override via kwargs model or model_id.
    """

    def __init__(self, model_id: str = "anthropic.claude-3-haiku-20240307-v1:0") -> None:
        self.model_id = model_id

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        # TODO
        raise NotImplementedError

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        # TODO
        raise NotImplementedError
        yield  # pragma: no cover


# Fake $/1K-token rates for arithmetic practice. NOT real prices.
# Replace with current docs as of August 2026 before any real forecast.
PLACEHOLDER_RATES_PER_1K: dict[str, dict[str, float]] = {
    "openai:gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # FAKE
    "anthropic:claude-haiku": {"input": 0.00025, "output": 0.00125},  # FAKE
    "bedrock:claude-haiku": {"input": 0.00025, "output": 0.00125},  # FAKE
    "ollama:local": {"input": 0.0, "output": 0.0},
}


def estimate_cost(
    provider_model: str,
    input_tokens: int,
    output_tokens: int,
    rates: dict[str, dict[str, float]] | None = None,
) -> float:
    """Rough USD estimate using placeholder per-1K rates.

    cost = (input_tokens/1000)*input_rate + (output_tokens/1000)*output_rate
    Raise KeyError if provider_model missing; ValueError on negative counts.
    """
    # TODO
    raise NotImplementedError


def estimate_weight_memory_bytes(num_params: int, bits_per_param: float) -> int:
    """Estimate weight storage: int(num_params * (bits_per_param / 8.0)).

    fp16 → bits_per_param=16; q4 → 4. Reject non-positive bits; negative params.
    """
    # TODO
    raise NotImplementedError


def get_client(provider: str, **kwargs: Any) -> LLMClient:
    """Factory: ollama | openai_stub | anthropic_stub | bedrock_stub."""
    # TODO: dispatch on provider name (case-insensitive); raise ValueError if unknown
    raise NotImplementedError
