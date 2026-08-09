"""Known-good CORE 204 checkpoint — frozen embed helpers for APP 305 / capstone.

Import pattern (from a lab under genai-gurukul-labs/):

    import sys
    from pathlib import Path
    CHECKPOINT = Path(__file__).resolve().parents[N] / "checkpoints" / "core-204"
    sys.path.insert(0, str(CHECKPOINT))
    from embedder import LocalEmbedder, cosine_similarity, rank_documents

Prefer this package over a learner's possibly-wrong `core-204/starter` unless
`GURUKUL_LAB=solution pytest core-204/tests -q` (or the learner's own green run)
has passed and the team explicitly opts into that code.
"""

from embedder import (
    Embedder,
    FixtureEmbedder,
    LocalEmbedder,
    OllamaEmbedder,
    cosine_similarity,
    default_embedder,
    negation_failure_demo,
    rank_documents,
)

__all__ = [
    "Embedder",
    "FixtureEmbedder",
    "LocalEmbedder",
    "OllamaEmbedder",
    "cosine_similarity",
    "default_embedder",
    "negation_failure_demo",
    "rank_documents",
]

__version__ = "204.0.0"
