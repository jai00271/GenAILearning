"""APP 305 — document ingestion helpers (solution).

Offline: markdown / text fixtures + a tiny fake PDF-table string parser.
No real PDF binary required — fixtures represent parser *output*.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_OCR_GARBAGE_RE = re.compile(r"[^\w\s.,;:/\-()%]+", re.UNICODE)
_TABLE_LINE_RE = re.compile(r"^\s*\|(.+)\|\s*$")


@dataclass
class Document:
    """One ingested source after parse + metadata extraction."""

    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: str = "text"  # markdown | table | ocr | text


def extract_metadata(source: str | Path, text: str) -> dict[str, Any]:
    """Extract light metadata from path + body.

    Fields: source, title, char_count, word_count, has_table, ocr_suspect.
    Title = first markdown H1 if present, else stem of filename.
    """
    path = Path(source)
    title = path.stem.replace("_", " ").replace("-", " ").strip()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break
    has_table = ("|" in text and "---" in text) or "TABLE:" in text.upper()
    return {
        "source": str(path),
        "title": title,
        "char_count": len(text),
        "word_count": len(_WORD_RE.findall(text)),
        "has_table": has_table,
        "ocr_suspect": is_ocr_junk(text),
    }


def is_ocr_junk(text: str) -> bool:
    """Heuristic: scanned/OCR residue looks noisy.

    Flags when (a) non-word symbol ratio is high, or (b) classic OCR markers
    appear (□, ﬁ ligature residue, 'rn'/'m' confusion markers we plant in fixtures),
    or (c) many isolated single-char tokens.
    Teaching heuristic — not a production OCR quality model.
    """
    if not text or not text.strip():
        return True
    cleaned = text.strip()
    if "OCR_JUNK" in cleaned.upper() or "□" in cleaned or "ﬁ" in cleaned:
        return True
    symbols = _OCR_GARBAGE_RE.findall(cleaned)
    ratio = len("".join(symbols)) / max(len(cleaned), 1)
    if ratio >= 0.08:
        return True
    tokens = _WORD_RE.findall(cleaned.lower())
    if not tokens:
        return True
    singles = sum(1 for t in tokens if len(t) == 1)
    return (singles / len(tokens)) >= 0.35


def parse_fake_pdf_table(raw: str) -> list[dict[str, str]]:
    """Parse a *fake PDF extract* that looks like pipe tables or TABLE blocks.

    Accepts either markdown-pipe tables or lines after a `TABLE:` marker with
    whitespace-separated columns on the header row.

    Returns a list of row dicts (header → cell). Raises ValueError if no rows
    can be parsed — models a parser failure mode callers must handle.
    """
    if not isinstance(raw, str):
        raise TypeError("raw must be a string")
    lines = [ln.rstrip() for ln in raw.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty table extract")

    # Prefer markdown pipe tables
    pipe_rows: list[list[str]] = []
    for ln in lines:
        m = _TABLE_LINE_RE.match(ln)
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        # skip separator rows like ---|---
        if all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells):
            continue
        pipe_rows.append(cells)

    if len(pipe_rows) >= 2:
        header = pipe_rows[0]
        out: list[dict[str, str]] = []
        for row in pipe_rows[1:]:
            padded = row + [""] * (len(header) - len(row))
            out.append({header[i]: padded[i] for i in range(len(header))})
        if out:
            return out

    # Fallback: TABLE: block with whitespace columns
    start = 0
    for i, ln in enumerate(lines):
        if ln.upper().startswith("TABLE:"):
            start = i + 1
            break
    block = lines[start:]
    if len(block) < 2:
        raise ValueError("no parseable table rows")
    header = block[0].split()
    if len(header) < 2:
        raise ValueError("table header too short")
    rows: list[dict[str, str]] = []
    for ln in block[1:]:
        if ln.startswith("---") or set(ln) <= {"-", " "}:
            continue
        parts = ln.split()
        if len(parts) < len(header):
            # ragged row — pad (enterprise messiness)
            parts = parts + [""] * (len(header) - len(parts))
        # if too many tokens, join extras into last column
        if len(parts) > len(header):
            parts = parts[: len(header) - 1] + [" ".join(parts[len(header) - 1 :])]
        rows.append({header[i]: parts[i] for i in range(len(header))})
    if not rows:
        raise ValueError("no parseable table rows")
    return rows


def table_rows_to_text(rows: list[dict[str, str]]) -> str:
    """Serialize parsed rows back to a markdown-pipe table for chunking."""
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def load_document(path: str | Path) -> Document:
    """Load one fixture file into a Document with metadata + kind."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    meta = extract_metadata(p, text)
    suffix = p.suffix.lower()
    name = p.name.lower()

    kind = "text"
    body = text
    if "ocr" in name or meta["ocr_suspect"]:
        kind = "ocr"
    elif "table" in name or suffix in {".pdftxt", ".table"} or meta["has_table"]:
        kind = "table"
        try:
            rows = parse_fake_pdf_table(text)
            body = (
                f"# {meta['title']}\n\n"
                f"(parsed table · {len(rows)} rows)\n\n"
                + table_rows_to_text(rows)
            )
            meta["table_rows"] = len(rows)
            meta["parse_ok"] = True
        except ValueError as exc:
            # Parser failure mode: keep raw text, flag failure
            meta["parse_ok"] = False
            meta["parse_error"] = str(exc)
            body = text
    elif suffix in {".md", ".markdown"}:
        kind = "markdown"

    meta["kind"] = kind
    return Document(doc_id=p.stem, text=body, metadata=meta, kind=kind)


def load_corpus(directory: str | Path) -> list[Document]:
    """Load all supported fixtures from a directory (non-recursive)."""
    d = Path(directory)
    if not d.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {d}")
    files = sorted(
        p
        for p in d.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".md", ".txt", ".pdftxt", ".table", ".markdown"}
        and not p.name.startswith(".")
        and p.name != "golden.jsonl"
    )
    return [load_document(p) for p in files]
