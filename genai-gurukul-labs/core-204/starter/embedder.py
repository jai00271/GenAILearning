"""CORE 204 — embeddings interface, cosine ranking, negation failure demo (starter).

Offline by default: implement LocalEmbedder as a deterministic hash/ngram
embedder so pytest never needs OpenAI, Cohere, or Ollama.

Optional later: GURUKUL_EMBEDDER=ollama with `nomic-embed-text` — see lesson.
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

    Spec (match solution so tests stay green):
    - Normalize text: lowercase, keep only [a-z0-9]+ tokens joined by spaces.
    - For each character n-gram length in [ngram_min, ngram_max], hash each gram
      with SHA-256. Bucket = first 4 little-endian bytes % dimensions.
      Sign = +1 if digest[4] bit0 is 0 else -1. Accumulate into a zero vector.
    - L2-normalize the vector (leave zeros if empty text / zero norm).
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
        # TODO: embed each text; return (len(texts), dimensions)
        raise NotImplementedError

    def _embed_one(self, text: str) -> np.ndarray:
        # TODO: feature-hashing n-gram bag; L2-normalize
        raise NotImplementedError


class FixtureEmbedder:
    """Lookup embedder for known strings; unknown texts fall back to LocalEmbedder."""

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
        if fallback is not None:
            self._fallback = fallback
        elif self._dim >= 8:
            self._fallback = LocalEmbedder(dimensions=self._dim)
        else:
            self._fallback = None

    @property
    def dimensions(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> np.ndarray:
        # TODO: table hit → copy vector; else fallback or zeros
        raise NotImplementedError


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Cosine similarity; 0.0 if either vector has zero L2 norm (FOUND 101 contract)."""
    # TODO
    raise NotImplementedError


def rank_documents(
    query: str,
    documents: list[str],
    embedder: Embedder | None = None,
) -> list[tuple[int, float]]:
    """Embed query + docs, return (doc_index, cosine) pairs sorted by score descending.

    Tie-break: lower document index first when scores are equal.
    Default embedder: LocalEmbedder().
    """
    # TODO
    raise NotImplementedError


def negation_failure_demo(embedder: Embedder | None = None) -> dict[str, float]:
    """Return cosine scores that document the negation / lexical-overlap failure.

    Use these exact strings (tests pin them):
      affirmative = "the authentication service is healthy"
      negated     = "the authentication service is not healthy"
      unrelated   = "quarterly cafeteria menu and catering schedule for building B"

    Return dict keys:
      sim_affirmative_negated, sim_affirmative_unrelated
    """
    # TODO
    raise NotImplementedError


def default_embedder() -> Embedder:
    """Factory: LocalEmbedder unless GURUKUL_EMBEDDER=ollama."""
    mode = os.environ.get("GURUKUL_EMBEDDER", "local").strip().lower()
    if mode == "ollama":
        return OllamaEmbedder()
    return LocalEmbedder()


class OllamaEmbedder:
    """Optional local neural embedder via Ollama HTTP API (nomic-embed-text).

    Provided so you can experiment offline with a real model after the lab.
    Tests do not call this class.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://127.0.0.1:11434",
        dimensions: int | None = None,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        if self._dimensions is None:
            probe = self.embed(["dimension probe"])
            self._dimensions = int(probe.shape[1])
        return self._dimensions

    def embed(self, texts: list[str]) -> np.ndarray:
        import json
        import urllib.error
        import urllib.request

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
                f"`{self._model}` pulled? Use LocalEmbedder for labs."
            ) from exc
        embeddings = body.get("embeddings")
        if not embeddings:
            raise RuntimeError("Ollama response missing embeddings")
        arr = np.asarray(embeddings, dtype=np.float64)
        if self._dimensions is None:
            self._dimensions = int(arr.shape[1])
        return arr
