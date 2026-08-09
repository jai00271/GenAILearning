# Checkpoint · CORE 204 — Embeddings & Vector Semantics

**Known-good** frozen helpers for later modules (APP 305 RAG, capstone). Later labs
should import from this checkpoint **by default**, not from a learner's possibly-wrong
`core-204/starter` code.

## What is frozen here

| Symbol | Role |
|---|---|
| `LocalEmbedder` | Deterministic hash/ngram embedder — offline, pytest-safe |
| `FixtureEmbedder` | Exact vector table + LocalEmbedder fallback |
| `cosine_similarity` | Zero-safe cosine (FOUND 101 contract) |
| `rank_documents` | Query → ranked `(index, score)` list |
| `negation_failure_demo` | Documents lexical/negation failure mode |
| `OllamaEmbedder` | Optional local neural path (`nomic-embed-text`) |
| `default_embedder` | `LocalEmbedder` unless `GURUKUL_EMBEDDER=ollama` |

This is **not** a production embedding model. It exists so ranking plumbing and
failure-mode tests stay reproducible. Swap in OpenAI / Cohere / Ollama only after
the plumbing is green.

## How APP 305 (and capstone) should import

From a file under `genai-gurukul-labs/app-305/...` (adjust `parents[N]` to reach
the labs root):

```python
import sys
from pathlib import Path

LABS_ROOT = Path(__file__).resolve().parents[2]  # tune depth as needed
CHECKPOINT = LABS_ROOT / "checkpoints" / "core-204"
sys.path.insert(0, str(CHECKPOINT))

from embedder import LocalEmbedder, cosine_similarity, rank_documents
# or: import embedder; from the package root after path insert
```

Package-style (same directory on `sys.path`):

```python
sys.path.insert(0, str(CHECKPOINT))
import embedder  # module
from embedder import rank_documents
```

If your packaging later installs labs as a proper package, prefer:

```python
# hypothetical future layout — not required today
from checkpoints.core_204 import LocalEmbedder, rank_documents
```

Until then, the `sys.path` insert above is the supported contract.

## When a learner may swap their own solution

A learner (or APP lab) may point at `core-204/solution` or a personal fork **only if**:

```bash
cd genai-gurukul-labs
GURUKUL_LAB=solution .venv/bin/pytest core-204/tests -q   # green
# or GURUKUL_LAB=starter after the learner filled TODOs — also green
```

Otherwise keep the checkpoint. Capstone / APP 305 CI should default to
`checkpoints/core-204/`.

## Optional Ollama path

```bash
ollama pull nomic-embed-text
GURUKUL_EMBEDDER=ollama python -c "from embedder import default_embedder; print(default_embedder().embed(['hello']).shape)"
```

Paid cloud APIs (OpenAI `text-embedding-3-*`, Cohere `embed-v4.0`) are documented on
the CORE 204 lesson page with `[PAID — approx cost]` labels. They are **not**
wired into this checkpoint on purpose.

## Version

`__version__ = "204.0.0"` — bump only if APP/capstone contracts change deliberately.
