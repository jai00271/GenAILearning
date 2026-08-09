"""Convergent checks for PROD 401 — FakeJudge, trajectory score, regression gate."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from judge import (  # noqa: E402
    FakeJudge,
    judge_human_disagreement,
    lexical_overlap_score,
)
from regression_gate import (  # noqa: E402
    regression_gate,
    summarize_prompt_tweak_regression,
)
from trajectory_score import score_trajectory  # noqa: E402


def test_lexical_overlap_basic():
    assert lexical_overlap_score("vpn reset steps", "vpn reset steps") == pytest.approx(1.0)
    assert lexical_overlap_score("vpn reset", "okta mfa policy") == pytest.approx(0.0)
    s = lexical_overlap_score("reset the vpn token", "vpn reset token guide")
    assert 0.0 < s < 1.0


def test_fake_judge_score_pass_fail():
    j = FakeJudge(mode="lexical")
    good = j.score_response(
        "Reset VPN by revoking the token then re-enrolling",
        "Reset VPN by revoking the token then re-enrolling",
    )
    assert good["label"] == "pass"
    assert good["score"] >= 0.5
    bad = j.score_response("hello world", "Reset VPN by revoking the token")
    assert bad["label"] == "fail"


def test_fake_judge_rejects_bad_mode():
    with pytest.raises(ValueError):
        FakeJudge(mode="vibes")


def test_position_bias_pairwise():
    j = FakeJudge(mode="position_biased", bias_position="A")
    # B is clearly better vs reference, but position bias picks A
    out = j.pairwise(
        "nope",
        "exact match reference answer here",
        reference="exact match reference answer here",
    )
    assert out["winner"] == "A"
    assert out["biased"] is True
    assert out["bias_kind"] == "position"

    j_b = FakeJudge(mode="position_biased", bias_position="B")
    out_b = j_b.pairwise("great answer with many tokens", "x")
    assert out_b["winner"] == "B"


def test_self_preference_pairwise():
    j = FakeJudge(mode="self_prefer", self_marker="[[MODEL_X]]")
    out = j.pairwise(
        "weak answer [[MODEL_X]]",
        "much better complete answer about vpn reset token",
        reference="vpn reset token",
    )
    assert out["winner"] == "A"
    assert out["biased"] is True
    assert out["bias_kind"] == "self_preference"


def test_lexical_pairwise_with_reference():
    j = FakeJudge(mode="lexical")
    out = j.pairwise(
        "vpn reset",
        "okta only",
        reference="vpn reset guide",
    )
    assert out["winner"] == "A"
    assert out["biased"] is False


def test_judge_human_disagreement_high_agreement():
    judge = ["pass", "pass", "fail", "pass", "pass"]
    human = ["pass", "pass", "fail", "pass", "fail"]
    result = judge_human_disagreement(judge, human)
    assert result["n"] == 5
    assert result["agreement"] == pytest.approx(0.8)
    assert result["disagreed_indices"] == [4]
    assert "spot_check_sample" in result["recommended_next"]


def test_judge_human_disagreement_triggers_human_loop():
    judge = ["pass", "pass", "pass", "pass"]
    human = ["fail", "fail", "fail", "pass"]
    result = judge_human_disagreement(judge, human)
    assert result["agreement"] == pytest.approx(0.25)
    assert 0 in result["disagreed_indices"]
    assert "pause_auto_ship" in result["recommended_next"]
    assert "adjudicate_disagreements_with_humans" in result["recommended_next"]
    assert "inspect_judge_rubric_and_bias" in result["recommended_next"]


def test_judge_human_length_mismatch():
    with pytest.raises(ValueError):
        judge_human_disagreement(["pass"], ["pass", "fail"])


def test_trajectory_perfect_path():
    events = [
        {"kind": "tool_call", "tool": "ticket_lookup", "args": {"ticket_id": "INC1"}},
        {"kind": "tool_call", "tool": "search_kb", "args": {"query": "vpn"}},
    ]
    expected = {
        "tools": [
            {"tool": "ticket_lookup", "args": {"ticket_id": "INC1"}},
            {"tool": "search_kb", "args": {"query": "vpn"}},
        ],
        "final_answer_ok": True,
    }
    result = score_trajectory(events, expected)
    assert result["passed"] is True
    assert result["tool_path_ok"] is True
    assert result["right_answer_wrong_tool"] is False
    assert result["right_tool_wrong_args"] is False
    assert result["has_extra_calls"] is False


def test_trajectory_right_answer_wrong_tool():
    events = [
        {"tool": "search_kb", "args": {"query": "vpn"}},
    ]
    expected = {
        "tools": [{"tool": "ticket_lookup", "args": {"ticket_id": "INC1"}}],
        "final_answer_ok": True,
    }
    result = score_trajectory(events, expected)
    assert result["passed"] is False
    assert result["right_answer_wrong_tool"] is True
    assert result["answer_score"] == 1.0
    assert result["wrong_tool_slots"] >= 1


def test_trajectory_right_tool_wrong_args():
    events = [
        {"name": "ticket_lookup", "arguments": {"ticket_id": "WRONG"}},
    ]
    expected = {
        "tools": [{"tool": "ticket_lookup", "args": {"ticket_id": "INC1"}}],
        "final_answer_ok": True,
    }
    result = score_trajectory(events, expected)
    assert result["passed"] is False
    assert result["right_tool_wrong_args"] is True
    assert result["wrong_args"] == 1
    assert result["matched_tools"] == 1


def test_trajectory_extra_calls():
    events = [
        {"tool": "ticket_lookup", "args": {"ticket_id": "INC1"}},
        {"tool": "search_kb", "args": {"query": "vpn"}},
        {"tool": "search_kb", "args": {"query": "vpn again"}},
    ]
    expected = {
        "tools": [
            {"tool": "ticket_lookup", "args": {"ticket_id": "INC1"}},
            {"tool": "search_kb", "args": {"query": "vpn"}},
        ],
        "final_answer_ok": True,
        "allow_extra": False,
    }
    result = score_trajectory(events, expected)
    assert result["has_extra_calls"] is True
    assert result["extra_calls"] == 1
    assert result["passed"] is False

    allowed = score_trajectory(events, {**expected, "allow_extra": True})
    assert allowed["has_extra_calls"] is False
    assert allowed["passed"] is True


def test_regression_gate_pass_and_fail():
    baseline = {"judge_agree": 0.82, "traj_overall": 0.90, "task_f1": 0.75}
    ok_cand = {"judge_agree": 0.80, "traj_overall": 0.91, "task_f1": 0.74}
    result = regression_gate(baseline, ok_cand, max_drop=0.05)
    assert result["passed"] is True
    assert result["drops"]["judge_agree"] == pytest.approx(0.02)

    bad_cand = {"judge_agree": 0.70, "traj_overall": 0.91, "task_f1": 0.75}
    bad = regression_gate(baseline, bad_cand, max_drop=0.05)
    assert bad["passed"] is False
    assert "judge_agree" in bad["failed_metrics"]


def test_regression_gate_required_missing():
    baseline = {"a": 1.0}
    candidate = {"b": 1.0}
    result = regression_gate(
        baseline, candidate, required_metrics=["a", "b"], max_drop=0.05
    )
    assert result["passed"] is False
    assert "a" in result["missing_metrics"] or "a" in result["failed_metrics"]
    assert "b" in result["missing_metrics"] or "b" in result["failed_metrics"]


def test_regression_gate_max_drop_validation():
    with pytest.raises(ValueError):
        regression_gate({"a": 1.0}, {"a": 1.0}, max_drop=0.0)


def test_summarize_prompt_tweak():
    baseline = {"x": 0.9}
    msg_ok = summarize_prompt_tweak_regression(baseline, {"x": 0.88}, max_drop=0.05)
    assert msg_ok.startswith("PASS")
    msg_bad = summarize_prompt_tweak_regression(baseline, {"x": 0.70}, max_drop=0.05)
    assert msg_bad.startswith("FAIL")
