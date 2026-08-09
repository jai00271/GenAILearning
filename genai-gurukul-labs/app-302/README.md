# APP 302 — LLM APIs & SDKs

Lesson: [`../../genai-gurukul/modules/app-302-llm-apis.html`](../../genai-gurukul/modules/app-302-llm-apis.html)

## What you build

Provider-agnostic thin interface:

- `complete(messages) -> str`
- `stream_tokens(messages) -> Iterator[str]`

Adapters:

| Adapter | Role |
|---|---|
| `OllamaClient` | **Default** — real `httpx` against Ollama `/api/chat` |
| `StubOpenAIClient` | Fake OpenAI — no `OPENAI_API_KEY` |
| `StubAnthropicClient` | Fake Anthropic — no SDK install |
| `StubBedrockClient` | Fake Bedrock Converse — no AWS creds |

Helpers:

- `estimate_cost` — arithmetic on **placeholder** $/1K rates (labeled FAKE; replace with current docs as of August 2026)
- `estimate_weight_memory_bytes` — `params × bits/8` for FP16 vs Q4 intuition

## Run tests

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest app-302/tests -q
# after filling starter TODOs:
GURUKUL_LAB=starter pytest app-302/tests -q
```

No cloud keys required for green CI. If `OPENAI_API_KEY` or AWS credentials are present, tests still use stubs by default (optional live skip marker exists).

## Optional live Ollama

```bash
ollama pull llama3.2
ollama serve   # if not already running
```

```python
from providers import OllamaClient
with OllamaClient(model="llama3.2") as c:
    print(c.complete([{"role": "user", "content": "Say hi in one word"}]))
```

## Optional paid extras (not in requirements.txt)

Default `pip install -r requirements.txt` stays light (`httpx` already listed). For real SDK experiments outside pytest:

```bash
pip install openai anthropic boto3
```

Treat OpenAI / Anthropic / Bedrock calls as **[PAID — approx cost]** — check current vendor pricing as of August 2026. Prefer Ollama for daily practice.
