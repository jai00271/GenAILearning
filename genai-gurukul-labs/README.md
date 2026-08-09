# GenAI Gurukul — companion labs

Hands-on half of **GenAI Gurukul**. Lesson HTML lives in [`../genai-gurukul/`](../genai-gurukul/). Portfolio-facing writeups (challenge memos, capstone docs) are **English**. Lesson pages are Hinglish.

## Setup

```bash
cd genai-gurukul-labs
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ollama is **not** required for FOUND 101–103 or CORE 201. Default local models for APP 301+ will be documented there. Assumption until confirmed: `llama3.2` and `nomic-embed-text`.

## How labs are graded

| Kind | Where | Success |
|---|---|---|
| Convergent | `<module>/starter` + adjacent `solution` + `tests` | `pytest` green |
| Debug / decision / track challenge | later tracks | rubric on the lesson page |

```bash
pytest found-101/tests found-102/tests found-103/tests core-201/tests -q
GURUKUL_LAB=solution pytest found-101/tests found-102/tests found-103/tests core-201/tests -q
```

## Module map (available)

- **FOUND 101** — NumPy cosine, `asyncio.gather`, Pydantic `ChatTurn`
- **FOUND 102** — Geometry, softmax + temperature, log-probs / perplexity
- **FOUND 103** — TinyMLP forward / backward intuition / train loop
- **CORE 201** — tiktoken counting, encoding compare, chat budget trim, toy BPE

## Layout

```
found-101/ … prod-406/     convergent modules
core-201/                  tokenization lab
checkpoints/               known-good snapshots (from CORE 204 onward)
challenges/                track gates — no starter, no solution
debug-labs/                broken systems, no TODO markers
capstone/                  CAP 501
```

Track 0 and CORE 201 are free/local. Later paid steps (Bedrock, SageMaker, OpenAI) are labeled on the lesson page with a local fallback where one exists.
