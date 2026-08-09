"""Convergent checks for APP 307 — MCP tools, ReAct loop, trajectory / max-steps."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from agent_loop import (  # noqa: E402
    CALCULATOR_DESCRIPTOR,
    TICKET_LOOKUP_DESCRIPTOR,
    AgentResult,
    FakeLLM,
    LLMResponse,
    ToolCall,
    ToolDescriptor,
    ToyMCPClient,
    calculator,
    run_react,
    summarize_trajectory,
    ticket_lookup,
)


def test_tool_descriptor_to_mcp_dict():
    d = ToolDescriptor(
        name="ping",
        description="health check",
        input_schema={"type": "object", "properties": {}},
    )
    m = d.to_mcp_dict()
    assert m["name"] == "ping"
    assert m["description"] == "health check"
    assert m["inputSchema"] == {"type": "object", "properties": {}}
    assert "input_schema" not in m


def test_calculator_and_ticket_lookup():
    assert calculator("(2+3)*4")["ok"] is True
    assert calculator("(2+3)*4")["value"] == 20
    bad = calculator("import os")
    assert bad["ok"] is False
    hit = ticket_lookup("inc1001")
    assert hit["ok"] is True
    assert hit["ticket"]["status"] == "in_progress"
    miss = ticket_lookup("INC9999")
    assert miss["ok"] is False
    assert miss["error"] == "not_found"


def test_mcp_list_and_call():
    mcp = ToyMCPClient()
    names = [t.name for t in mcp.list_tools()]
    assert names == sorted(names)
    assert "calculator" in names and "ticket_lookup" in names
    calc = mcp.call_tool("calculator", {"expression": "10/2"})
    assert calc["ok"] is True and calc["value"] == 5.0
    ticket = mcp.call_tool("ticket_lookup", {"ticket_id": "INC1002"})
    assert ticket["ok"] is True
    assert ticket["ticket"]["assignee"] == "iam"
    unknown = mcp.call_tool("nope", {})
    assert unknown["ok"] is False
    assert unknown["error"] == "unknown_tool"


def test_mcp_descriptors_match_constants():
    mcp = ToyMCPClient()
    by_name = {t.name: t for t in mcp.list_tools()}
    assert by_name["calculator"].input_schema == CALCULATOR_DESCRIPTOR.input_schema
    assert by_name["ticket_lookup"].description == TICKET_LOOKUP_DESCRIPTOR.description
    listed = [t.to_mcp_dict() for t in mcp.list_tools()]
    assert all("inputSchema" in row for row in listed)


def test_react_calculator_happy_path():
    llm = FakeLLM(
        script=[
            LLMResponse(
                tool_calls=(
                    ToolCall(
                        id="c1",
                        name="calculator",
                        arguments={"expression": "2+2"},
                    ),
                )
            ),
            LLMResponse(content="The answer is 4."),
        ]
    )
    mcp = ToyMCPClient()
    result = run_react("What is 2+2?", llm=llm, mcp=mcp, max_steps=5)
    assert isinstance(result, AgentResult)
    assert result.halted is False
    assert result.final_answer == "The answer is 4."
    kinds = [s.kind for s in result.trajectory]
    assert "tool_call" in kinds
    assert "tool_result" in kinds
    assert "final" in kinds
    assert result.steps_used == 2


def test_react_ticket_then_answer():
    llm = FakeLLM(
        script=[
            LLMResponse(
                tool_calls=(
                    ToolCall(
                        id="t1",
                        name="ticket_lookup",
                        arguments={"ticket_id": "INC1001"},
                    ),
                )
            ),
            LLMResponse(content="INC1001 is in_progress: VPN disconnects on split-tunnel"),
        ]
    )
    result = run_react("Status of INC1001?", llm=llm, mcp=ToyMCPClient(), max_steps=4)
    assert result.halted is False
    assert "in_progress" in (result.final_answer or "")
    tool_results = [s for s in result.trajectory if s.kind == "tool_result"]
    assert tool_results
    assert tool_results[0].detail["result"]["ticket"]["id"] == "INC1001"


def test_max_steps_circuit_breaker():
    # Model keeps requesting tools forever — breaker must halt.
    forever = [
        LLMResponse(
            tool_calls=(
                ToolCall(id=f"c{i}", name="calculator", arguments={"expression": "1+1"}),
            )
        )
        for i in range(20)
    ]
    llm = FakeLLM(script=forever)
    result = run_react("loop", llm=llm, mcp=ToyMCPClient(), max_steps=3)
    assert result.halted is True
    assert result.halt_reason == "max_steps"
    assert result.final_answer is None
    assert result.steps_used == 3
    assert any(s.kind == "halt" for s in result.trajectory)


def test_tool_error_logged_not_crash():
    llm = FakeLLM(
        script=[
            LLMResponse(
                tool_calls=(
                    ToolCall(
                        id="bad",
                        name="ticket_lookup",
                        arguments={"ticket_id": "INC0000"},
                    ),
                )
            ),
            LLMResponse(content="Ticket not found."),
        ]
    )
    result = run_react("missing ticket", llm=llm, mcp=ToyMCPClient(), max_steps=5)
    assert result.halted is False
    assert result.final_answer == "Ticket not found."
    errors = [s for s in result.trajectory if s.kind == "error"]
    assert len(errors) >= 1
    assert errors[0].detail["result"]["error"] == "not_found"


def test_unknown_tool_in_loop():
    llm = FakeLLM(
        script=[
            LLMResponse(
                tool_calls=(ToolCall(id="x", name="drop_table", arguments={}),)
            ),
            LLMResponse(content="I cannot do that."),
        ]
    )
    result = run_react("hack", llm=llm, mcp=ToyMCPClient(), max_steps=4)
    assert result.final_answer == "I cannot do that."
    assert any(s.kind == "error" for s in result.trajectory)


def test_summarize_trajectory_eval_beat():
    llm = FakeLLM(
        script=[
            LLMResponse(
                tool_calls=(
                    ToolCall(id="c1", name="calculator", arguments={"expression": "3*3"}),
                )
            ),
            LLMResponse(content="9"),
        ]
    )
    result = run_react("3*3", llm=llm, mcp=ToyMCPClient(), max_steps=5)
    summary = summarize_trajectory(result.trajectory)
    assert summary["n_steps_logged"] == len(result.trajectory)
    assert summary["counts_by_kind"]["tool_call"] >= 1
    assert summary["counts_by_kind"]["final"] == 1
    assert "calculator" in summary["tool_names_called"]
    assert summary["had_error"] is False
    assert summary["hit_max_steps"] is False


def test_run_react_rejects_bad_max_steps():
    with pytest.raises(ValueError):
        run_react("x", llm=FakeLLM(script=[LLMResponse(content="hi")]), mcp=ToyMCPClient(), max_steps=0)


def test_fake_llm_script_and_heuristic():
    scripted = FakeLLM(script=[LLMResponse(content="done")])
    assert scripted.complete([{"role": "user", "content": "hi"}]).content == "done"

    auto = FakeLLM()
    first = auto.complete([{"role": "user", "content": "Please compute 7*8"}])
    assert first.has_tool_calls
    assert first.tool_calls[0].name == "calculator"
    second = auto.complete(
        [
            {"role": "user", "content": "Please compute 7*8"},
            {"role": "tool", "content": "{'value': 56}"},
        ]
    )
    assert second.content is not None
    assert not second.has_tool_calls
