"""Convergent checks for CORE 201."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import tiktoken

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from budget import fit_messages, message_tokens, total_tokens  # noqa: E402
from compare import compare_encodings  # noqa: E402
from counting import count_tokens, encode_ids  # noqa: E402
from toy_bpe import apply_merges, learn_merges, word_to_symbols  # noqa: E402

RUNBOOK = (
    "Check INC0042817: restart the auth pod, then reset the service account password."
)


def test_count_tokens_matches_tiktoken():
    enc = tiktoken.get_encoding("cl100k_base")
    expected = len(enc.encode(RUNBOOK))
    assert count_tokens(RUNBOOK, "cl100k_base") == expected
    assert encode_ids(RUNBOOK, "cl100k_base") == list(enc.encode(RUNBOOK))


def test_compare_encodings_returns_both_and_positive():
    got = compare_encodings(RUNBOOK, ["cl100k_base", "o200k_base"])
    assert set(got) == {"cl100k_base", "o200k_base"}
    assert got["cl100k_base"] > 0
    assert got["o200k_base"] > 0
    # Sanity: both encodings should be in a similar ballpark for short English+ID text
    assert abs(got["cl100k_base"] - got["o200k_base"]) < got["cl100k_base"]


def test_message_framing_and_fit_drops_oldest():
    encoding = "cl100k_base"
    messages = [
        {"role": "system", "content": "You are an IT ops copilot."},
        {"role": "user", "content": "List open incidents."},
        {"role": "assistant", "content": "INC0042817 is open."},
        {"role": "user", "content": "Walk me through the password reset runbook."},
    ]
    full = total_tokens(messages, encoding)
    assert full == sum(message_tokens(m, encoding) for m in messages) + 3

    # Tight budget forces dropping from the front while keeping the last user turn.
    tight = message_tokens(messages[-1], encoding) + 3 + 20
    fitted = fit_messages(messages, encoding, tight)
    assert fitted[-1] == messages[-1]
    assert len(fitted) < len(messages)
    assert total_tokens(fitted, encoding) <= tight


def test_fit_messages_raises_if_last_alone_too_big():
    encoding = "cl100k_base"
    huge = {"role": "user", "content": "word " * 500}
    with pytest.raises(ValueError):
        fit_messages([huge], encoding, token_budget=10)


def test_toy_bpe_learns_and_applies_deterministically():
    corpus = ["low", "lowest", "newer", "wider"]
    assert word_to_symbols("low") == ["l", "o", "w", "</w>"]
    merges = learn_merges(corpus, num_merges=5)
    assert len(merges) == 5
    # Determinism: same corpus → same merges
    assert learn_merges(corpus, 5) == merges
    encoded = apply_merges("lowest", merges)
    assert isinstance(encoded, list)
    assert "".join(encoded).replace("</w>", "") == "lowest"
    # After merges, should be fewer symbols than raw characters+eow
    assert len(encoded) < len(word_to_symbols("lowest"))
