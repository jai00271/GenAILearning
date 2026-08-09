"""APP 305 — document ingestion helpers (starter).

Offline: markdown / text fixtures + a tiny fake PDF-table string parser.
No real PDF binary required — fixtures represent parser *output*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Document:
    """One ingested source after parse + metadata extraction."""

    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: str = "text"  # markdown | table | ocr | text


def extract_metadata(source: str | Path, text: str) -> dict[str, Any]:
    """Extract light metadata: source, title, char_count, word_count, has_table, ocr_suspect."""
    # TODO: implement metadata extraction (title from H1 or filename stem)
    raise NotImplementedError


def is_ocr_junk(text: str) -> bool:
    """Heuristic OCR/scanned-junk detector. See solution docstring for flags."""
    # TODO: implement OCR junk heuristic
    raise NotImplementedError


def parse_fake_pdf_table(raw: str) -> list[dict[str, str]]:
    """Parse pipe tables or TABLE: blocks into row dicts. Empty/unparseable → ValueError."""
    # TODO: implement fake PDF table parser
    raise NotImplementedError


def table_rows_to_text(rows: list[dict[str, str]]) -> str:
    """Serialize parsed rows to a stable text block."""
    # TODO: serialize header + rows
    raise NotImplementedError


def load_document(path: str | Path) -> Document:
    """Load one fixture file into a Document with metadata + kind."""
    # TODO: read file, set kind (markdown/table/ocr), parse tables when applicable
    raise NotImplementedError


def load_corpus(directory: str | Path) -> list[Document]:
    """Load all supported fixtures from a directory (non-recursive)."""
    # TODO: iterate supported suffixes, skip golden.jsonl
    raise NotImplementedError
