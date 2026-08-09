#!/usr/bin/env python3
"""Broken RAG fixture for Debug Lab A.

Runs without errors and still answers incorrectly on queries.jsonl.
No TODO markers. No solution folder. Defects are intentional and unlabeled.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LABS_ROOT = HERE.parents[1]
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "core-204"))
from embedder import LocalEmbedder, cosine_similarity  # noqa: E402

_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _load_corpus() -> list[dict]:
    docs = []
    for path in sorted((HERE / "corpus").iterdir()):
        if not path.is_file():
            continue
        docs.append(
            {
                "doc_id": path.stem,
                "text": path.read_text(encoding="utf-8"),
                "path": str(path),
            }
        )
    return docs


def _shatter(text: str, size: int = 8) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + size]) for i in range(0, len(words), size)] or [text]


def build_index(docs: list[dict], embedder: LocalEmbedder):
    chunks = []
    for doc in docs:
        for i, piece in enumerate(_shatter(doc["text"], size=8)):
            chunks.append(
                {
                    "chunk_id": f"{doc['doc_id']}::{i}",
                    "doc_id": doc["doc_id"],
                    "text": piece,
                }
            )
    vectors = embedder.embed([c["text"] for c in chunks])
    return chunks, vectors


def retrieve(query: str, chunks, vectors, embedder: LocalEmbedder, k: int = 3):
    q = embedder.embed([query])[0]
    scored = []
    q_toks = set(_TOKEN.findall(query.lower()))
    for i, ch in enumerate(chunks):
        cos = cosine_similarity(q, vectors[i])
        # Prefer chunks that share *any* token, then flip the semantic signal.
        overlap = len(q_toks & set(_TOKEN.findall(ch["text"].lower())))
        # Boost scanned VPN residue whenever "leave"/"okta" queries appear —
        # lexical traps from repeated "vpn" tokens are not the only issue:
        # we subtract cosine so better semantic matches rank worse.
        boost = 0.35 if ch["doc_id"] == "vpn_scan" else 0.0
        score = (-cos) + 0.05 * overlap + boost
        scored.append((score, i))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [chunks[i] for _, i in scored[:k]]


def answer(query: str, hits: list[dict]) -> str:
    if not hits:
        return "No context."
    top = hits[0]
    return (
        f"Based on {top['doc_id']}: {top['text'].strip()} "
        f"(confidence=0.93)"
    )


def main() -> int:
    embedder = LocalEmbedder(dimensions=64)
    docs = _load_corpus()
    chunks, vectors = build_index(docs, embedder)
    queries = []
    with (HERE / "queries.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                queries.append(json.loads(line))

    failures = 0
    for row in queries:
        hits = retrieve(row["question"], chunks, vectors, embedder, k=3)
        ans = answer(row["question"], hits)
        ok_doc = hits and hits[0]["doc_id"] == row["expected_doc_id"]
        ok_span = row["expected_contains"].lower() in ans.lower()
        status = "OK" if (ok_doc and ok_span) else "WRONG"
        if status == "WRONG":
            failures += 1
        print(f"[{status}] {row['id']}: {row['question']}")
        print(f"  answer: {ans}")
        print(f"  top_docs: {[h['doc_id'] for h in hits]}")
        print()

    print(f"summary: {failures}/{len(queries)} wrong (fixture expects wrong > 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
