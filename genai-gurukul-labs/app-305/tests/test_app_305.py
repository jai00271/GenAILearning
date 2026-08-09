"""Convergent checks for APP 305 — RAG deep-dive (ingest · chunk · retrieve)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from chunk import chunk_fixed, chunk_structure_aware  # noqa: E402
from ingest import (  # noqa: E402
    is_ocr_junk,
    load_corpus,
    load_document,
    parse_fake_pdf_table,
)
from retrieve import (  # noqa: E402
    embed_chunks,
    hybrid_search,
    keyword_search,
    mean_precision_recall_at_k,
    retrieve_doc_ids,
    semantic_search,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"

LABS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "core-204"))
sys.path.insert(0, str(LABS_ROOT / "checkpoints" / "app-304"))
from embedder import LocalEmbedder  # noqa: E402
from golden import load_golden_jsonl  # noqa: E402


@pytest.fixture(scope="module")
def corpus():
    return load_corpus(FIXTURES)


@pytest.fixture(scope="module")
def embedder():
    return LocalEmbedder(dimensions=64)


def test_load_corpus_kinds(corpus):
    by_id = {d.doc_id: d for d in corpus}
    assert set(by_id) >= {"okta_reset", "auth_health", "leave_table", "vpn_scanned"}
    assert by_id["okta_reset"].kind == "markdown"
    assert by_id["leave_table"].kind == "table"
    assert by_id["vpn_scanned"].kind == "ocr"
    assert by_id["leave_table"].metadata.get("parse_ok") is True
    assert by_id["leave_table"].metadata.get("table_rows", 0) >= 3
    assert "Parental" in by_id["leave_table"].text
    assert by_id["okta_reset"].metadata["title"].lower().startswith("okta")


def test_ocr_junk_fixture_flagged():
    raw = (FIXTURES / "vpn_scanned.txt").read_text(encoding="utf-8")
    assert is_ocr_junk(raw) is True
    clean = (FIXTURES / "okta_reset.md").read_text(encoding="utf-8")
    assert is_ocr_junk(clean) is False


def test_parse_fake_pdf_table_pipe_and_failure():
    raw = (FIXTURES / "leave_table.pdftxt").read_text(encoding="utf-8")
    rows = parse_fake_pdf_table(raw)
    assert any(r.get("LeaveType") == "Parental" for r in rows)
    parental = next(r for r in rows if r.get("LeaveType") == "Parental")
    assert parental["MaxDays"] == "90"
    with pytest.raises(ValueError):
        parse_fake_pdf_table("no tables here at all")


def test_fixed_vs_structure_on_table():
    doc = load_document(FIXTURES / "leave_table.pdftxt")
    fixed = chunk_fixed(doc, size=12, overlap=2)
    structured = chunk_structure_aware(doc, prose_size=12, overlap=2)
    assert len(fixed) >= 2
    # Structure-aware should keep a chunk that contains both LeaveType header and Parental
    assert any(
        ("LeaveType" in c.text or "Leave type" in c.text.lower() or "Annual" in c.text)
        and "Parental" in c.text
        for c in structured
    )
    # Fixed tiny windows often split header from parental row
    assert not any(
        "LeaveType" in c.text and "Parental" in c.text and "Sick" in c.text
        for c in fixed
    ) or len(fixed) > len([c for c in structured if c.metadata.get("block") == "table"])


def test_structure_quarantines_ocr():
    doc = load_document(FIXTURES / "vpn_scanned.txt")
    chunks = chunk_structure_aware(doc)
    assert len(chunks) == 1
    assert chunks[0].metadata.get("quarantine") is True


def test_hybrid_retrieval_beats_chance(corpus, embedder):
    # Structure-aware index
    chunks = []
    for doc in corpus:
        chunks.extend(chunk_structure_aware(doc, prose_size=40, overlap=10))
    vectors = embed_chunks(chunks, embedder)
    golden = load_golden_jsonl(FIXTURES / "golden.jsonl")

    ranked = [
        retrieve_doc_ids(
            row["question"],
            chunks,
            vectors,
            mode="hybrid",
            embedder=embedder,
            k=3,
        )
        for row in golden
    ]
    rels = [row["relevant_ids"] for row in golden]
    metrics = mean_precision_recall_at_k(ranked, rels, k=3)
    # Eval beat gates for this tiny fixture set
    assert metrics["recall"] >= 0.75
    assert metrics["precision"] >= 0.25
    # Parental leave query must hit leave_table in top-3
    q2 = next(r for r in golden if r["id"] == "q2")
    hit = retrieve_doc_ids(
        q2["question"], chunks, vectors, mode="hybrid", embedder=embedder, k=3
    )
    assert "leave_table" in hit


def test_semantic_and_keyword_return_ids(corpus, embedder):
    chunks = []
    for doc in corpus:
        if doc.kind == "ocr":
            continue
        chunks.extend(chunk_structure_aware(doc))
    vectors = embed_chunks(chunks, embedder)
    q = "reset Okta password email link"
    sem = semantic_search(q, chunks, vectors, embedder=embedder, k=3)
    kw = keyword_search(q, chunks, k=3)
    hyb = hybrid_search(q, chunks, vectors, embedder=embedder, k=3)
    assert len(sem) >= 1 and all(isinstance(x, str) for x in sem)
    assert len(kw) >= 1
    assert len(hyb) >= 1


def test_mean_precision_recall_helper_matches_manual():
    ranked = [["leave_table", "okta_reset"], ["auth_health"]]
    rels = [["leave_table"], ["auth_health", "x"]]
    out = mean_precision_recall_at_k(ranked, rels, k=2)
    # q1: P=1/2, R=1/1; q2: P=1/2, R=1/2 → mean P=0.5, mean R=0.75
    assert out["precision"] == pytest.approx(0.5)
    assert out["recall"] == pytest.approx(0.75)
