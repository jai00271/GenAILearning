#!/usr/bin/env python3
"""Debug Lab B — Agent cost incident (unbounded tool loop).

Runs cleanly and burns a fake token/USD budget by never stopping.
No TODO markers. No solution folder. Defects are intentional and unlabeled.
Deepened in PROD 404 (observability & cost). Linked from APP 307.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent


@dataclass
class Meter:
    """Fake cost meter — each LLM turn and tool call adds spend."""

    llm_calls: int = 0
    tool_calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    usd: float = 0.0
    events: list[dict] = field(default_factory=list)

    def charge_llm(self, prompt_chars: int, completion_chars: int) -> None:
        # Rough stand-in: 4 chars ≈ 1 token; $0.002 / 1k tokens blended
        tin = max(1, prompt_chars // 4)
        tout = max(1, completion_chars // 4)
        self.llm_calls += 1
        self.tokens_in += tin
        self.tokens_out += tout
        burn = (tin + tout) / 1000.0 * 0.002
        self.usd += burn
        self.events.append(
            {"kind": "llm", "tokens_in": tin, "tokens_out": tout, "usd": round(burn, 6)}
        )

    def charge_tool(self, name: str) -> None:
        self.tool_calls += 1
        burn = 0.0004  # flat per-tool surcharge (API / MCP hop)
        self.usd += burn
        self.events.append({"kind": "tool", "name": name, "usd": burn})


def calculator(expression: str) -> dict:
    try:
        # Intentionally permissive for the incident fixture — not the APP 307 lab.
        value = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return {"ok": True, "value": value}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def run_unbounded_agent(goal: str, *, soft_budget_usd: float = 0.05) -> dict:
    """ReAct-shaped loop that *looks* like it has a budget but does not enforce it.

    The model stub always requests another calculator call. A comment near the
    budget check suggests a halt — behavior disagrees. Learners RCA the burn.
    """
    meter = Meter()
    trajectory: list[dict] = []
    messages = [{"role": "user", "content": goal}]
    step = 0
    # Soft budget is logged only — not a hard stop (the incident).
    while True:
        step += 1
        prompt_blob = json.dumps(messages)
        # Model "thinks" it still needs to verify the sum with one more tool call.
        completion = json.dumps(
            {
                "tool_calls": [
                    {
                        "name": "calculator",
                        "arguments": {"expression": f"{step}+{step}"},
                    }
                ]
            }
        )
        meter.charge_llm(len(prompt_blob), len(completion))
        trajectory.append({"step": step, "kind": "tool_call", "expression": f"{step}+{step}"})

        meter.charge_tool("calculator")
        result = calculator(f"{step}+{step}")
        messages.append({"role": "tool", "content": json.dumps(result)})
        trajectory.append({"step": step, "kind": "tool_result", "result": result})

        # Budget "guard" — logs a warning but continues. Classic cost incident.
        if meter.usd >= soft_budget_usd:
            trajectory.append(
                {
                    "step": step,
                    "kind": "budget_warning",
                    "usd": round(meter.usd, 6),
                    "soft_budget_usd": soft_budget_usd,
                    "action": "continue",  # <-- should have been halt
                }
            )

        # Escape hatch only for the demo runner so the process ends.
        # Production bug: this ceiling is set absurdly high vs the soft budget.
        if step >= 200:
            trajectory.append({"step": step, "kind": "hard_cap", "reason": "demo_process_cap"})
            break

    return {
        "goal": goal,
        "steps": step,
        "usd": round(meter.usd, 6),
        "llm_calls": meter.llm_calls,
        "tool_calls": meter.tool_calls,
        "tokens_in": meter.tokens_in,
        "tokens_out": meter.tokens_out,
        "soft_budget_usd": soft_budget_usd,
        "budget_exceeded": meter.usd >= soft_budget_usd,
        "trajectory_tail": trajectory[-8:],
        "n_budget_warnings": sum(1 for t in trajectory if t.get("kind") == "budget_warning"),
    }


def main() -> int:
    report = run_unbounded_agent(
        "What is 2+2? Verify carefully before answering.",
        soft_budget_usd=0.05,
    )
    out_path = HERE / "incident_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== Debug Lab B · agent cost incident ===")
    print(f"steps={report['steps']}  usd={report['usd']}  soft_budget={report['soft_budget_usd']}")
    print(f"llm_calls={report['llm_calls']}  tool_calls={report['tool_calls']}")
    print(f"budget_exceeded={report['budget_exceeded']}  warnings={report['n_budget_warnings']}")
    print(f"wrote {out_path}")
    print()
    print("Expected: budget_exceeded True, many warnings, no early halt.")
    print("RCA tip: soft budget does not stop the loop; hard_cap is 200 steps.")
    print("PROD 404 deepens meters / quotas / kill-switches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
