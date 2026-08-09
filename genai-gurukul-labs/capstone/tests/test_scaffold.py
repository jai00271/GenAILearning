"""Structure checks for CAP 501 capstone scaffold (not full AWS deploy)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_has_acceptance_table_and_fails_lambda_demo():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Acceptance criteria" in text or "acceptance" in text.lower()
    assert "Recall@5" in text
    assert "0.60" in text
    assert "TTFT" in text
    assert "failover" in text.lower()
    assert "chat with" in text.lower() and "lambda" in text.lower()
    assert "fail" in text.lower()


def test_architecture_doc_exists():
    assert (ROOT / "architecture.md").is_file()


def test_corpus_has_at_least_three_formats():
    fixtures = ROOT / "corpus" / "fixtures"
    assert fixtures.is_dir()
    suffixes = {p.suffix.lower() for p in fixtures.iterdir() if p.is_file()}
    assert ".md" in suffixes
    assert ".json" in suffixes
    assert ".html" in suffixes
    readme = (ROOT / "corpus" / "README.md").read_text(encoding="utf-8")
    assert "expand" in readme.lower() or "10k" in readme.lower()


def test_app_prod_stubs_exist():
    app = ROOT / "app"
    for name in ("main.py", "auth.py", "rate_limit.py", "failover.py", "tracing.py"):
        path = app / name
        assert path.is_file(), f"missing {path}"
        body = path.read_text(encoding="utf-8")
        assert len(body.strip()) > 40


def test_app_main_wires_stubs():
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "require_api_key" in main or "auth" in main
    assert "limiter" in main or "rate_limit" in main
    assert "trace_span" in main or "tracing" in main
    assert "failover" in main.lower()
    assert "FastAPI" in main


def test_golden_set_at_least_40():
    path = ROOT / "eval" / "golden_set.jsonl"
    assert path.is_file()
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        assert "id" in obj and "query" in obj
        assert "relevant_doc_ids" in obj
        assert isinstance(obj["relevant_doc_ids"], list)
        rows.append(obj)
    assert len(rows) >= 40


def test_writeup_templates_exist():
    writeups = ROOT / "writeups"
    for name in ("eval_report.md", "cost_model.md", "failure_modes.md"):
        text = (writeups / name).read_text(encoding="utf-8")
        assert len(text.strip()) > 80
    fm = (writeups / "failure_modes.md").read_text(encoding="utf-8").lower()
    assert "indirect" in fm and "injection" in fm
    assert "cost" in fm and ("blowup" in fm or "blow-up" in fm)


def test_interview_english_onepagers_exist():
    interview = ROOT / "interview"
    for name in (
        "presenting-capstone.md",
        "system-design-onepager.md",
        "genai-interview-bank.md",
    ):
        assert (interview / name).is_file()
        assert len((interview / name).read_text(encoding="utf-8").strip()) > 80


def test_rate_limit_and_failover_logic_without_fastapi():
    """Import stubs that do not require FastAPI installed."""
    import importlib.util
    import sys

    def load(mod_name: str, path: Path):
        spec = importlib.util.spec_from_file_location(mod_name, path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        return mod

    rate = load("cap_rate_limit", ROOT / "app" / "rate_limit.py")
    lim = rate.RateLimitStub(max_per_minute=2)
    assert lim.allow("k", now=1000.0) is True
    assert lim.allow("k", now=1001.0) is True
    assert lim.allow("k", now=1002.0) is False

    fail = load("cap_failover", ROOT / "app" / "failover.py")
    ans, path = fail.complete_with_failover(
        fail.primary_stub, fail.secondary_stub, "FORCE_FAIL please"
    )
    assert path == "failover"
    assert "failover" in ans.lower() or "unavailable" in ans.lower()
