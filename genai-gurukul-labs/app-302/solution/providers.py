"""APP 302 — LLM client interface, Ollama (httpx), cloud stubs, cost + quantization helpers.

Solution implementation. Pytest needs no cloud keys; Ollama is exercised via httpx MockTransport
in tests. Optional live path: run `ollama serve` and use OllamaClient against localhost.
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

    Docs: https://docs.ollama.com/api/chat
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
        msgs = _require_messages(messages)
        model = str(kwargs.get("model", self.model))
        payload = {"model": model, "messages": msgs, "stream": False}
        resp = self._client.post(f"{self.base_url}/api/chat", json=payload)
        resp.raise_for_status()
        body = resp.json()
        message = body.get("message") or {}
        content = message.get("content")
        if content is None:
            raise RuntimeError("Ollama response missing message.content")
        return str(content)

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        msgs = _require_messages(messages)
        model = str(kwargs.get("model", self.model))
        payload = {"model": model, "messages": msgs, "stream": True}
        with self._client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                event = json.loads(line)
                message = event.get("message") or {}
                piece = message.get("content")
                if piece:
                    yield str(piece)
                if event.get("done"):
                    break


class StubOpenAIClient:
    """Deterministic OpenAI-shaped stub — no network, no API key."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        msgs = _require_messages(messages)
        last = msgs[-1]["content"]
        return f"[openai:{kwargs.get('model', self.model)}] {last}"

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        text = self.complete(messages, **kwargs)
        for word in text.split(" "):
            yield word + " "


class StubAnthropicClient:
    """Deterministic Anthropic Messages-shaped stub — no network."""

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        self.model = model

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        msgs = _require_messages(messages)
        last = msgs[-1]["content"]
        return f"[anthropic:{kwargs.get('model', self.model)}] {last}"

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        text = self.complete(messages, **kwargs)
        for i in range(0, len(text), 8):
            yield text[i : i + 8]


class StubBedrockClient:
    """Deterministic Bedrock Converse-shaped stub — no AWS creds."""

    def __init__(self, model_id: str = "anthropic.claude-3-haiku-20240307-v1:0") -> None:
        self.model_id = model_id

    def complete(self, messages: Sequence[Message], **kwargs: Any) -> str:
        msgs = _require_messages(messages)
        last = msgs[-1]["content"]
        mid = str(kwargs.get("model", kwargs.get("model_id", self.model_id)))
        return f"[bedrock:{mid}] {last}"

    def stream_tokens(self, messages: Sequence[Message], **kwargs: Any) -> Iterator[str]:
        yield self.complete(messages, **kwargs)


# ---------------------------------------------------------------------------
# Cost estimator — PLACEHOLDER rates only (replace with current vendor docs)
# ---------------------------------------------------------------------------

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

    `provider_model` keys into PLACEHOLDER_RATES_PER_1K (or caller-supplied table).
    Rates are clearly fake — replace with current docs before budgeting.
    """
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be non-negative")
    table = rates if rates is not None else PLACEHOLDER_RATES_PER_1K
    if provider_model not in table:
        raise KeyError(
            f"unknown provider_model {provider_model!r}; "
            "add a row or pass rates=... (placeholder table only)"
        )
    row = table[provider_model]
    return (input_tokens / 1000.0) * float(row["input"]) + (output_tokens / 1000.0) * float(
        row["output"]
    )


def estimate_weight_memory_bytes(num_params: int, bits_per_param: float) -> int:
    """Estimate weight storage: params × bits / 8.

    Examples: fp16 → 16 bits; q4 → 4 bits. Ignores KV cache / optimizer states.
    """
    if num_params < 0:
        raise ValueError("num_params must be non-negative")
    if bits_per_param <= 0:
        raise ValueError("bits_per_param must be positive")
    return int(num_params * (bits_per_param / 8.0))


def get_client(provider: str, **kwargs: Any) -> LLMClient:
    """Factory: ollama (default) | openai_stub | anthropic_stub | bedrock_stub."""
    key = provider.strip().lower()
    if key in {"ollama", "local"}:
        return OllamaClient(**kwargs)
    if key in {"openai", "openai_stub", "stub_openai"}:
        return StubOpenAIClient(**kwargs)
    if key in {"anthropic", "anthropic_stub", "stub_anthropic"}:
        return StubAnthropicClient(**kwargs)
    if key in {"bedrock", "bedrock_stub", "stub_bedrock"}:
        return StubBedrockClient(**kwargs)
    raise ValueError(f"unknown provider {provider!r}")
