"""Convergent checks for APP 302 — LLM APIs & SDKs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from providers import (  # noqa: E402
    PLACEHOLDER_RATES_PER_1K,
    OllamaClient,
    StubAnthropicClient,
    StubBedrockClient,
    StubOpenAIClient,
    estimate_cost,
    estimate_weight_memory_bytes,
    get_client,
)


def _ollama_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        body = json.loads(request.content.decode("utf-8"))
        assert body["model"]
        assert body["messages"]
        if body.get("stream"):
            chunks = [
                json.dumps({"message": {"role": "assistant", "content": "Hel"}, "done": False}),
                json.dumps({"message": {"role": "assistant", "content": "lo"}, "done": False}),
                json.dumps({"message": {"role": "assistant", "content": ""}, "done": True}),
            ]
            return httpx.Response(200, text="\n".join(chunks) + "\n")
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "Hello from Ollama stub"}},
        )

    return httpx.MockTransport(handler)


def test_ollama_complete_via_httpx_mock():
    client = httpx.Client(transport=_ollama_transport())
    llm = OllamaClient(client=client, base_url="http://ollama.test")
    out = llm.complete([{"role": "user", "content": "hi"}])
    assert out == "Hello from Ollama stub"
    client.close()


def test_ollama_stream_tokens_via_httpx_mock():
    client = httpx.Client(transport=_ollama_transport())
    llm = OllamaClient(client=client, base_url="http://ollama.test")
    pieces = list(llm.stream_tokens([{"role": "user", "content": "hi"}]))
    assert pieces == ["Hel", "lo"]
    assert "".join(pieces) == "Hello"
    client.close()


def test_ollama_rejects_empty_messages():
    client = httpx.Client(transport=_ollama_transport())
    llm = OllamaClient(client=client, base_url="http://ollama.test")
    with pytest.raises(ValueError):
        llm.complete([])
    client.close()


def test_stub_openai_complete_and_stream():
    stub = StubOpenAIClient(model="gpt-4o-mini")
    msgs = [{"role": "user", "content": "ping"}]
    assert stub.complete(msgs) == "[openai:gpt-4o-mini] ping"
    streamed = "".join(stub.stream_tokens(msgs)).strip()
    assert "ping" in streamed
    assert streamed.startswith("[openai:")


def test_stub_anthropic_and_bedrock():
    a = StubAnthropicClient(model="claude-haiku")
    b = StubBedrockClient(model_id="amazon.titan-text-express-v1")
    msgs = [{"role": "user", "content": "status"}]
    assert a.complete(msgs) == "[anthropic:claude-haiku] status"
    assert b.complete(msgs) == "[bedrock:amazon.titan-text-express-v1] status"
    assert "".join(a.stream_tokens(msgs)) == a.complete(msgs)
    assert list(b.stream_tokens(msgs)) == [b.complete(msgs)]


def test_estimate_cost_placeholder_rates():
    src = (ROOT / LAB / "providers.py").read_text(encoding="utf-8").lower()
    assert "fake" in src and "replace with current docs" in src
    assert "openai:gpt-4o-mini" in PLACEHOLDER_RATES_PER_1K
    cost = estimate_cost("openai:gpt-4o-mini", input_tokens=1000, output_tokens=1000)
    expected = (
        PLACEHOLDER_RATES_PER_1K["openai:gpt-4o-mini"]["input"]
        + PLACEHOLDER_RATES_PER_1K["openai:gpt-4o-mini"]["output"]
    )
    assert cost == pytest.approx(expected)
    assert estimate_cost("ollama:local", 5000, 5000) == 0.0
    with pytest.raises(KeyError):
        estimate_cost("nope:model", 1, 1)
    with pytest.raises(ValueError):
        estimate_cost("ollama:local", -1, 0)


def test_estimate_weight_memory_fp16_vs_q4():
    n = 7_000_000_000
    fp16 = estimate_weight_memory_bytes(n, 16)
    q4 = estimate_weight_memory_bytes(n, 4)
    assert fp16 == n * 2
    assert q4 == n // 2
    assert q4 * 4 == fp16
    with pytest.raises(ValueError):
        estimate_weight_memory_bytes(10, 0)


def test_get_client_factory_stubs():
    assert isinstance(get_client("openai_stub"), StubOpenAIClient)
    assert isinstance(get_client("anthropic_stub"), StubAnthropicClient)
    assert isinstance(get_client("bedrock_stub"), StubBedrockClient)
    with pytest.raises(ValueError):
        get_client("unknown-provider")


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Optional live OpenAI — skipped without OPENAI_API_KEY (CI stays green)",
)
def test_optional_live_openai_skipped_without_key():
    """Present only so learners with a key can extend; default CI never runs body."""
    pytest.skip("Live OpenAI not wired in convergent lab — use stubs")
