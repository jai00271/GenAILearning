# GenAI Gurukul — companion labs

Hands-on half of **GenAI Gurukul**. Lesson HTML lives in [`../genai-gurukul/`](../genai-gurukul/). Portfolio-facing writeups (challenge memos, capstone docs) are **English**. Lesson pages are Hinglish.

## Setup

```bash
cd genai-gurukul-labs
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ollama is **not** required for FOUND 101–103 or CORE 201–204 convergent labs (CORE 204 uses a deterministic local embedder; optional Ollama path is documented on the lesson). Assumption for APP 301+: `llama3.2` and `nomic-embed-text` until confirmed. **APP 302** defaults to an httpx Ollama client with MockTransport in pytest (no live server required); cloud OpenAI/Anthropic/Bedrock adapters are stubs so CI needs no keys.

## How labs are graded

| Kind | Where | Success |
|---|---|---|
| Convergent | `<module>/starter` + adjacent `solution` + `tests` | `pytest` green |
| Debug / decision / track challenge | later tracks | rubric on the lesson page |

```bash
GURUKUL_LAB=solution pytest found-*/tests core-20*/tests app-30*/tests -q
```

## Module map (available)

- **FOUND 101** — NumPy cosine, `asyncio.gather`, Pydantic `ChatTurn`
- **FOUND 102** — Geometry, softmax + temperature, log-probs / perplexity
- **FOUND 103** — TinyMLP forward / backward intuition / train loop
- **CORE 201** — tiktoken counting, encoding compare, chat budget trim, toy BPE
- **CORE 202** — scaled dot-product attention, causal mask, multi-head (NumPy)
- **CORE 203** — mean NLL / perplexity + toy DPO-style preference loss
- **CORE 204** — LocalEmbedder, cosine rank, negation failure demo; checkpoint under `checkpoints/core-204/`
- **CORE challenge** — `challenges/core/` (no starter/solution; rubric-graded English memo)
- **APP 301** — Ollama-only prompts, few-shot, structured JSON + Pydantic, user-typed injection heuristics (FakeCompleter in tests)
- **APP 302** — thin `LLMClient` (`complete` / `stream_tokens`), Ollama httpx + cloud stubs, cost + quantization memory helpers
- **APP 303** — conversation memory under token budget + window vs retrieve_later placement

## Layout

```
found-101/ … prod-406/     convergent modules
checkpoints/               known-good snapshots (from CORE 204 onward)
challenges/                track gates — no starter, no solution
debug-labs/                broken systems, no TODO markers
capstone/                  CAP 501
```

Paid cloud steps (Bedrock, SageMaker, OpenAI) are labeled on lesson pages with a local fallback where one exists.
