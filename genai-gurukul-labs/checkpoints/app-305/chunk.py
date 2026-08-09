"""APP 305 — chunking strategies (solution).

Fixed-size vs structure-aware (tables kept intact; OCR quarantined).
Simplification: word-count windows stand in for token windows (CORE 201 reminder:
production chunkers should count tokens, not characters/words).
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


def _words(text: str) -> list[str]:
    return text.split()


def chunk_fixed(
    doc: Document,
    size: int = 40,
    overlap: int = 10,
) -> list[Chunk]:
    """Fixed-size word windows with overlap.

    Splits blindly — will fracture tables mid-row. Useful as a baseline that
    structure-aware chunking should beat on table queries.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")

    words = _words(doc.text)
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    step = size - overlap
    while start < len(words):
        window = words[start : start + size]
        text = " ".join(window)
        chunks.append(
            Chunk(
                chunk_id=f"{doc.doc_id}::fixed::{idx}",
                doc_id=doc.doc_id,
                text=text,
                metadata={
                    **doc.metadata,
                    "strategy": "fixed",
                    "start_word": start,
                    "n_words": len(window),
                },
            )
        )
        idx += 1
        if start + size >= len(words):
            break
        start += step
    return chunks


def _split_prose_and_tables(text: str) -> list[tuple[str, str]]:
    """Return list of (kind, block) where kind is 'prose' or 'table'."""
    lines = text.splitlines()
    blocks: list[tuple[str, str]] = []
    buf: list[str] = []
    in_table = False

    def flush(kind: str) -> None:
        nonlocal buf
        body = "\n".join(buf).strip()
        if body:
            blocks.append((kind, body))
        buf = []

    for ln in lines:
        is_pipe = ln.strip().startswith("|") and "|" in ln.strip()[1:]
        if is_pipe and not in_table:
            flush("prose")
            in_table = True
            buf.append(ln)
        elif is_pipe and in_table:
            buf.append(ln)
        elif in_table and not is_pipe:
            flush("table")
            in_table = False
            buf.append(ln)
        else:
            buf.append(ln)
    flush("table" if in_table else "prose")
    return blocks


def chunk_structure_aware(
    doc: Document,
    prose_size: int = 40,
    overlap: int = 10,
) -> list[Chunk]:
    """Keep tables as single chunks; fixed-window the prose; quarantine OCR.

    - kind == ocr or ocr_suspect → one low-trust chunk (not split further)
    - table blocks (pipe rows) → one chunk per table
    - remaining prose → chunk_fixed-style windows
    """
    if doc.kind == "ocr" or doc.metadata.get("ocr_suspect"):
        return [
            Chunk(
                chunk_id=f"{doc.doc_id}::ocr::0",
                doc_id=doc.doc_id,
                text=doc.text.strip(),
                metadata={
                    **doc.metadata,
                    "strategy": "structure_aware",
                    "trust": "low",
                    "quarantine": True,
                },
            )
        ]

    # Whole-document table extracts: keep as one chunk even if prose wrappers exist.
    if doc.kind == "table" and doc.metadata.get("parse_ok"):
        return [
            Chunk(
                chunk_id=f"{doc.doc_id}::table::0",
                doc_id=doc.doc_id,
                text=doc.text.strip(),
                metadata={
                    **doc.metadata,
                    "strategy": "structure_aware",
                    "block": "table",
                    "trust": "high",
                },
            )
        ]

    chunks: list[Chunk] = []
    idx = 0
    for kind, block in _split_prose_and_tables(doc.text):
        if kind == "table":
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}::table::{idx}",
                    doc_id=doc.doc_id,
                    text=block,
                    metadata={
                        **doc.metadata,
                        "strategy": "structure_aware",
                        "block": "table",
                        "trust": "high",
                    },
                )
            )
            idx += 1
            continue

        # Prose: reuse fixed windows on a temporary Document
        prose_doc = Document(
            doc_id=doc.doc_id,
            text=block,
            metadata=doc.metadata,
            kind=doc.kind,
        )
        for fixed in chunk_fixed(prose_doc, size=prose_size, overlap=overlap):
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}::prose::{idx}",
                    doc_id=doc.doc_id,
                    text=fixed.text,
                    metadata={
                        **doc.metadata,
                        "strategy": "structure_aware",
                        "block": "prose",
                        "trust": "normal",
                    },
                )
            )
            idx += 1
    return chunks
