# GenAI Gurukul — companion labs

Lesson HTML: [`../genai-gurukul/`](../genai-gurukul/). Portfolio writeups: **English**. Lessons: Hinglish.

## Setup

```bash
cd genai-gurukul-labs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Most convergent labs are offline (FakeCompleter / MockTransport / NumPy). Ollama assumed later for live runs: `llama3.2`, `nomic-embed-text` (confirm locally).

## Run everything

```bash
GURUKUL_LAB=solution pytest found-*/tests core-20*/tests app-30*/tests prod-40*/tests capstone/tests -q
```

## Layout

```
found-101/ … prod-406/   convergent starter + solution + tests
checkpoints/             known-good (core-204, app-304, app-305, …)
challenges/{core,app,prod}/   no starter, no solution — rubric gates
debug-labs/
  A-broken-rag/
  B-agent-cost-incident/
capstone/                CAP 501 scaffold + interview materials
```

## Track gates

Score yourself against the published 4-dimension rubric (avg ≥ 3, no dimension < 2) before starting the next track. Banner appears on challenge pages and the first page of the next track.
