"""Known-good APP 305 checkpoint — frozen ingest/chunk/retrieve helpers.

Import pattern (from labs root children):

    import sys
    from pathlib import Path
    CHECKPOINT = Path(__file__).resolve().parents[N] / "checkpoints" / "app-305"
    sys.path.insert(0, str(CHECKPOINT))
    from ingest import load_corpus, parse_fake_pdf_table
    from chunk import chunk_structure_aware
    from retrieve import hybrid_search, mean_precision_recall_at_k

Prefer this over a learner's possibly-wrong `app-305/starter` unless their tests are green.
"""

from chunk import Chunk, chunk_fixed, chunk_structure_aware
from ingest import (
    Document,
    extract_metadata,
    is_ocr_junk,
    load_corpus,
    load_document,
    parse_fake_pdf_table,
    table_rows_to_text,
)
from retrieve import (
    chunk_ids_to_doc_ids,
    embed_chunks,
    hybrid_search,
    keyword_search,
    mean_precision_recall_at_k,
    retrieve_doc_ids,
    semantic_search,
)

__all__ = [
    "Chunk",
    "Document",
    "chunk_fixed",
    "chunk_ids_to_doc_ids",
    "chunk_structure_aware",
    "embed_chunks",
    "extract_metadata",
    "hybrid_search",
    "is_ocr_junk",
    "keyword_search",
    "load_corpus",
    "load_document",
    "mean_precision_recall_at_k",
    "parse_fake_pdf_table",
    "retrieve_doc_ids",
    "semantic_search",
    "table_rows_to_text",
]

__version__ = "305.0.0"
