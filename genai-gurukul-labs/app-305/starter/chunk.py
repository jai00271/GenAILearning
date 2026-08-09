"""APP 305 — chunking strategies (starter).

Fixed-size vs structure-aware (tables kept intact; OCR quarantined).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ingest import Document


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


def chunk_fixed(
    doc: Document,
    size: int = 40,
    overlap: int = 10,
) -> list[Chunk]:
    """Fixed-size word windows with overlap. size>0; 0 <= overlap < size."""
    # TODO: implement fixed word-window chunking
    raise NotImplementedError


def chunk_structure_aware(
    doc: Document,
    prose_size: int = 40,
    overlap: int = 10,
) -> list[Chunk]:
    """Keep tables intact; quarantine OCR; fixed-window prose."""
    # TODO: implement structure-aware chunking
    raise NotImplementedError
