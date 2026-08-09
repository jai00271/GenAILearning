"""APP 301 — Completer protocol + local Ollama HTTP client (solution).

Cost: free/local. Talks to Ollama at http://localhost:11434 — no OpenAI /
Anthropic / Bedrock SDKs. Pytest should inject a FakeCompleter instead of
hitting a live server.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import httpx

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


@runtime_checkable
class Completer(Protocol):
    """Minimal chat completion interface for dependency injection."""

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
    ) -> str:
        """Return assistant text for the given chat messages."""
        ...


class OllamaCompleter:
    """Real client: POST /api/chat with stream=false via httpx.

    See https://docs.ollama.com/api/chat — messages use role/content objects.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
    ) -> str:
        if not messages:
            raise ValueError("messages must be non-empty")
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise ValueError("each message needs role and content")

        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
        }
        client = self._client or httpx.Client(timeout=self.timeout)
        try:
            response = client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
        finally:
            if self._owns_client and self._client is None:
                client.close()

        message = data.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str):
            raise RuntimeError("Ollama response missing message.content string")
        return content

    def close(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
            self._client = None

    def __enter__(self) -> OllamaCompleter:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
            self._owns_client = True
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
