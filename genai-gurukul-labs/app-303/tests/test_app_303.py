"""Convergent checks for APP 303 — context & memory engineering."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from memory import (  # noqa: E402
    ConversationMemory,
    FakeSummarizer,
    count_tokens,
    message_tokens,
    total_tokens,
)
from placement import decide_placement  # noqa: E402


def test_framing_matches_core_201_shape():
    encoding = "cl100k_base"
    msg = {"role": "user", "content": "Check INC0042817 auth pod."}
    expected = 4 + count_tokens("user", encoding) + count_tokens(msg["content"], encoding)
    assert message_tokens(msg, encoding) == expected
    assert total_tokens([msg], encoding) == expected + 3


def test_fake_summarizer_is_deterministic():
    msgs = [
        {"role": "user", "content": "List open incidents."},
        {"role": "assistant", "content": "INC0042817 is open and paging on-call."},
    ]
    s = FakeSummarizer()
    a = s.summarize(msgs)
    b = s.summarize(msgs)
    assert a == b
    assert a.startswith("SUMMARY[2]:")
    assert "user:" in a and "assistant:" in a
    assert s.summarize([]) == "SUMMARY: (empty)"


def test_memory_appends_under_budget_without_compaction():
    mem = ConversationMemory(token_budget=500, keep_recent=2)
    mem.append("system", "You are an IT ops copilot.")
    mem.append("user", "What is open?")
    mem.append("assistant", "INC0042817.")
    assert len(mem.messages()) == 3
    assert mem.token_count() <= 500
    assert mem.messages()[0]["role"] == "system"


def test_memory_compacts_when_over_budget():
    # Tiny budget forces summarization of older turns while keeping recent ones.
    mem = ConversationMemory(token_budget=90, keep_recent=2, summarizer=FakeSummarizer())
    mem.append("system", "You are an IT ops copilot for ACME.")
    mem.append("user", "Walk me through the password reset runbook step by step carefully.")
    mem.append(
        "assistant",
        "First verify the employee identity in Okta, then reset the service account password.",
    )
    mem.append("user", "Also check INC0042817 severity and last comment.")
    mem.append("assistant", "INC0042817 is SEV2; last comment says auth pods CrashLooping.")

    msgs = mem.messages()
    assert mem.token_count() <= 90
    # Leading system preserved; a SUMMARY system message appears; last 2 kept.
    assert msgs[0]["role"] == "system"
    assert msgs[0]["content"].startswith("You are an IT ops")
    summary_msgs = [m for m in msgs if m["role"] == "system" and m["content"].startswith("SUMMARY")]
    assert len(summary_msgs) == 1
    assert msgs[-2]["role"] == "user"
    assert "INC0042817" in msgs[-2]["content"]
    assert msgs[-1]["role"] == "assistant"


def test_memory_raises_if_cannot_fit():
    mem = ConversationMemory(token_budget=30, keep_recent=1)
    with pytest.raises(ValueError):
        mem.append("user", "word " * 80)


@pytest.mark.parametrize(
    "item,expected",
    [
        ({"kind": "live_ticket", "id": "INC0042817"}, "window"),
        ({"kind": "session_goal"}, "window"),
        ({"kind": "user_pref", "key": "region"}, "window"),
        ({"kind": "runbook", "title": "password-reset"}, "retrieve_later"),
        ({"kind": "wiki_page"}, "retrieve_later"),
        ({"kind": "pii_note", "label": "employee-phone"}, "retrieve_later"),
        ({"kind": "audit_log_blob"}, "retrieve_later"),
        # sensitivity override beats a window-friendly kind
        ({"kind": "live_ticket", "sensitivity": "pii"}, "retrieve_later"),
        ({"kind": "Live_Ticket"}, "window"),  # case-insensitive kind
    ],
)
def test_decide_placement_table(item, expected):
    assert decide_placement(item) == expected


def test_decide_placement_rejects_unknown():
    with pytest.raises(ValueError):
        decide_placement({"kind": "mystery_blob"})
    with pytest.raises(ValueError):
        decide_placement({})
