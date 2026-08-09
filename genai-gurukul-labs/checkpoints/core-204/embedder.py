"""CORE 204 checkpoint — frozen embeddings helpers (known-good).

Identical contract to the lab solution. APP 305 / capstone should import from
this package by default (see README.md). Offline LocalEmbedder for tests;
optional GURUKUL_EMBEDDER=ollama → OllamaEmbedder (nomic-embed-text).
"""

from __future__ import annotations

import hashlib
import os
import re
from typing import Protocol, runtime_checkable

import numpy as np

_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


@runtime_checkable
class Embedder(Protocol):
    """Minimal embed interface — APP 305 can swap LocalEmbedder for a real model."""

    @property
    def dimensions(self) -> int: ...

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return shape (len(texts), dimensions) float64 array."""
        ...


class LocalEmbedder:
    """Deterministic character-ngram hashed embedding (offline / pytest).

    Not a semantic model — it is a fixture-grade stand-in so ranking and
    failure demos stay reproducible without network or GPU.
    """

    def __init__(self, dimensions: int = 64, ngram_min: int = 3, ngram_max: int = 5) -> None:
        if dimensions < 8:
            raise ValueError("dimensions must be >= 8")
        if ngram_min < 1 or ngram_max < ngram_min:
            raise ValueError("invalid ngram range")
        self._dimensions = dimensions
        self._ngram_min = ngram_min
        self._ngram_max = ngram_max

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dimensions), dtype=np.float64)
        rows = [self._embed_one(t) for t in texts]
        return np.stack(rows, axis=0)

    def _embed_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self._dimensions, dtype=np.float64)
        normalized = " ".join(_WORD_RE.findall(text.lower()))
        if not normalized:
            return vec
        # Character n-grams over the normalized string (spaces kept as separators).
        for n in range(self._ngram_min, self._ngram_max + 1):
            if len(normalized) < n:
                continue
            for i in range(len(normalized) - n + 1):
                gram = normalized[i : i + n]
                digest = hashlib.sha256(gram.encode("utf-8")).digest()
                # Two signed feature hashes (feature hashing trick)
                bucket = int.from_bytes(digest[:4], "little") % self._dimensions
                sign = 1.0 if (digest[4] & 1) == 0 else -1.0
                vec[bucket] += sign
        norm = float(np.linalg.norm(vec))
        if norm == 0.0:
            return vec
        return vec / norm


class FixtureEmbedder:
    """Lookup embedder for known strings; unknown texts fall back to LocalEmbedder.

    Useful when a lesson wants exact vector geometry without inventing semantics.
    """

    def __init__(
        self,
        table: dict[str, list[float] | np.ndarray],
        fallback: LocalEmbedder | None = None,
    ) -> None:
        if not table:
            raise ValueError("table must be non-empty")
        dims = {len(np.asarray(v).ravel()) for v in table.values()}
        if len(dims) != 1:
            raise ValueError("all fixture vectors must share the same dimension")
        self._dim = dims.pop()
        self._table = {k: np.asarray(v, dtype=np.float64).ravel() for k, v in table.items()}
        self._fallback = fallback or LocalEmbedder(dimensions=self._dim)

    @property
    def dimensions(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> np.ndarray:
        rows: list[np.ndarray] = []
        for t in texts:
            if t in self._table:
                rows.append(self._table[t].copy())
            else:
                rows.append(self._fallback.embed([t])[0])
        return np.stack(rows, axis=0)


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Cosine similarity; 0.0 if either vector has zero L2 norm (FOUND 101 contract)."""
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def rank_documents(
    query: str,
    documents: list[str],
    embedder: Embedder | None = None,
) -> list[tuple[int, float]]:
    """Embed query + docs, return (doc_index, cosine) pairs sorted by score descending."""
    if embedder is None:
        embedder = LocalEmbedder()
    if not documents:
        return []
    q_vec = embedder.embed([query])[0]
    doc_vecs = embedder.embed(list(documents))
    scored = [(i, cosine_similarity(q_vec, doc_vecs[i])) for i in range(len(documents))]
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored


def negation_failure_demo(embedder: Embedder | None = None) -> dict[str, float]:
    """Show that lexical-overlap embeddings confuse affirmation with negation.

    With LocalEmbedder (hash n-grams), "… is healthy" and "… is not healthy"
    share almost all grams, so they score closer than a genuinely different topic.
    Real neural embeddings often soften — but do not eliminate — this failure mode
    for short negations and antonyms. Tests assert the naive failure honestly.
    """
    if embedder is None:
        embedder = LocalEmbedder()
    affirmative = "the authentication service is healthy"
    negated = "the authentication service is not healthy"
    unrelated = "quarterly cafeteria menu and catering schedule for building B"
    vectors = embedder.embed([affirmative, negated, unrelated])
    sim_neg = cosine_similarity(vectors[0], vectors[1])
    sim_unrelated = cosine_similarity(vectors[0], vectors[2])
    return {
        "sim_affirmative_negated": sim_neg,
        "sim_affirmative_unrelated": sim_unrelated,
    }


def default_embedder() -> Embedder:
    """Factory: LocalEmbedder unless GURUKUL_EMBEDDER=ollama (optional offline GPU/CPU)."""
    mode = os.environ.get("GURUKUL_EMBEDDER", "local").strip().lower()
    if mode == "ollama":
        return OllamaEmbedder()
    return LocalEmbedder()


class OllamaEmbedder:
    """Optional local neural embedder via Ollama HTTP API (nomic-embed-text).

    Not required for pytest. Pull model: `ollama pull nomic-embed-text`.
    Docs: https://ollama.com/library/nomic-embed-text
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://127.0.0.1:11434",
        dimensions: int | None = None,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._dimensions = dimensions  # discovered on first call if None

    @property
    def dimensions(self) -> int:
        if self._dimensions is None:
            probe = self.embed(["dimension probe"])
            self._dimensions = int(probe.shape[1])
        return self._dimensions

    def embed(self, texts: list[str]) -> np.ndarray:
        import urllib.error
        import urllib.request
        import json

        if not texts:
            dim = self._dimensions or 768
            return np.zeros((0, dim), dtype=np.float64)
        payload = json.dumps({"model": self._model, "input": texts}).encode("utf-8")
        req = urllib.request.Request(
            f"{self._base_url}/api/embed",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Ollama embed failed — is `ollama serve` running and "
                f"`{self._model}` pulled? Falling back is LocalEmbedder for labs."
            ) from exc
        embeddings = body.get("embeddings")
        if not embeddings:
            raise RuntimeError("Ollama response missing embeddings")
        arr = np.asarray(embeddings, dtype=np.float64)
        if self._dimensions is None:
            self._dimensions = int(arr.shape[1])
        return arr
