"""Convergent checks for APP 308 — shared catalog, graph edges, trajectory merge."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from orchestrator import (  # noqa: E402
    SharedToolCatalog,
    ToolSpec,
    TrajectoryEvent,
    build_default_catalog,
    merge_trajectories,
    run_supervisor_graph,
    trajectory_eval_summary,
)


def test_catalog_register_list_and_call():
    cat = SharedToolCatalog()
    cat.register(
        ToolSpec(
            name="echo",
            description="Echo text",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        ),
        lambda **kw: {"ok": True, "text": kw.get("text")},
    )
    names = [t.name for t in cat.list_tools()]
    assert names == ["echo"]
    mcp = cat.list_mcp()
    assert mcp[0]["name"] == "echo"
    assert "inputSchema" in mcp[0]
    assert cat.call("echo", {"text": "hi"}) == {"ok": True, "text": "hi"}
    miss = cat.call("nope", {})
    assert miss["ok"] is False
    assert miss["error"] == "unknown_tool"


def test_catalog_rejects_empty_name():
    cat = SharedToolCatalog()
    with pytest.raises(ValueError):
        cat.register(
            ToolSpec(name="", description="x", input_schema={}),
            lambda **kw: {"ok": True},
        )


def test_allowlist_hides_and_blocks_tools():
    cat = build_default_catalog()
    all_names = {t.name for t in cat.list_tools()}
    assert all_names >= {"search_kb", "ticket_lookup", "summarize_notes"}

    view = cat.allowlist(["ticket_lookup"])
    assert [t.name for t in view.list_tools()] == ["ticket_lookup"]
    ok = view.call("ticket_lookup", {"ticket_id": "INC1001"})
    assert ok.get("ok") is True
    blocked = view.call("search_kb", {"query": "vpn"})
    assert blocked["ok"] is False
    assert blocked["error"] == "unknown_tool"
    # Parent catalog still has search_kb
    assert cat.call("search_kb", {"query": "vpn"}).get("ok") is True


def test_merge_trajectories_orders_by_seq():
    ev = [
        TrajectoryEvent(seq=3, agent_id="b", kind="message"),
        TrajectoryEvent(seq=1, agent_id="a", kind="route"),
        TrajectoryEvent(seq=2, agent_id="a", kind="tool_call", detail={"name": "x"}),
    ]
    merged = merge_trajectories(ev)
    assert [e.seq for e in merged] == [1, 2, 3]
    assert merged[1].detail["name"] == "x"


def test_run_graph_ticket_and_research_path():
    result = run_supervisor_graph(
        "How do I fix VPN issues on INC1001?",
        max_hops=12,
    )
    assert result["final_answer"]
    assert result["final_answer"].startswith("MERGED:")
    assert "ticket" in result["worker_outputs"]
    assert "research" in result["worker_outputs"]
    assert "supervisor" in result["path"]
    assert "merge" in result["path"]
    assert result["halted"] is False

    traj = result["trajectory"]
    assert traj == sorted(traj, key=lambda e: e["seq"])
    agents = {e["agent_id"] for e in traj}
    assert "supervisor" in agents
    assert "worker_ticket" in agents or "worker_research" in agents

    summary = trajectory_eval_summary(traj)
    assert summary["n_events"] == len(traj)
    assert summary["tool_names_called"]
    assert "ticket_lookup" in summary["tool_names_called"] or "search_kb" in summary[
        "tool_names_called"
    ]
    assert "supervisor" in summary["agents_seen"]


def test_run_graph_research_only():
    result = run_supervisor_graph("What is the okta MFA policy tip?", max_hops=10)
    assert result["final_answer"]
    assert "research" in result["worker_outputs"]
    assert result["halted"] is False
    summary = trajectory_eval_summary(result["trajectory"])
    assert "search_kb" in summary["tool_names_called"]


def test_run_graph_rejects_empty_goal():
    with pytest.raises(ValueError):
        run_supervisor_graph("   ")


def test_worker_cannot_call_sibling_tools_via_allowlist():
    """Ticket worker allowlist must not expose search_kb (shared catalog lesson)."""
    cat = build_default_catalog()
    ticket_view = cat.allowlist(["ticket_lookup", "summarize_notes"])
    assert "search_kb" not in {t.name for t in ticket_view.list_tools()}
    assert ticket_view.call("search_kb", {"query": "vpn"})["error"] == "unknown_tool"
