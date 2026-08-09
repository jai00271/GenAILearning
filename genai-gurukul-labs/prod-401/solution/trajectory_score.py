"""PROD 401 — multi-step agent trajectory scoring (solution).

Scores tool paths beyond final-answer correctness:
- right answer, wrong tool
- right tool, wrong args
- extra / missing calls
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def _norm_args(args: Mapping[str, Any] | None) -> dict[str, Any]:
    if not args:
        return {}
    # Stable stringify for nested values
    return {str(k): args[k] for k in sorted(args, key=lambda x: str(x))}


def score_trajectory(
    events: Sequence[Mapping[str, Any]],
    expected: Mapping[str, Any],
) -> dict[str, object]:
    """Score an agent trajectory against an expected tool plan.

    Parameters
    ----------
    events
        Ordered tool-call events. Each may include ``tool`` / ``name`` and
        ``args`` / ``arguments``. Non-tool events (messages) are ignored.
    expected
        ``{"tools": [{"tool": str, "args": dict}, ...],
          "final_answer_ok": bool,
          "allow_extra": bool (default False)}``

    Returns
    -------
    dict with component flags/scores and an overall ``passed`` bool.
    Teaching labels include ``right_answer_wrong_tool``,
    ``right_tool_wrong_args``, and ``extra_calls``.
    """
    if not isinstance(expected, Mapping):
        raise TypeError("expected must be a mapping")

    planned = list(expected.get("tools") or [])
    final_ok = bool(expected.get("final_answer_ok", False))
    allow_extra = bool(expected.get("allow_extra", False))

    calls: list[dict[str, Any]] = []
    for ev in events:
        if not isinstance(ev, Mapping):
            continue
        kind = str(ev.get("kind", "tool_call")).lower()
        if kind not in {"tool_call", "tool", "call"}:
            # Also accept bare tool fields without kind
            if "tool" not in ev and "name" not in ev:
                continue
        tool = ev.get("tool") or ev.get("name")
        if not tool:
            continue
        args = ev.get("args") if "args" in ev else ev.get("arguments")
        if args is None:
            args = {}
        if not isinstance(args, Mapping):
            raise TypeError("tool args must be a mapping")
        calls.append({"tool": str(tool), "args": _norm_args(args)})

    n_expected = len(planned)
    n_actual = len(calls)

    # Align by index for ordered plan (teaching convention)
    matched_tools = 0
    wrong_args = 0
    wrong_tool_slots = 0
    for i, plan in enumerate(planned):
        plan_tool = str(plan.get("tool") or plan.get("name") or "")
        plan_args = _norm_args(plan.get("args") or plan.get("arguments") or {})
        if i >= len(calls):
            wrong_tool_slots += 1  # missing call counts as tool miss
            continue
        actual = calls[i]
        if actual["tool"] == plan_tool:
            matched_tools += 1
            if actual["args"] != plan_args:
                wrong_args += 1
        else:
            wrong_tool_slots += 1

    extra_calls = max(0, n_actual - n_expected)
    missing_calls = max(0, n_expected - n_actual)

    tool_path_ok = (
        wrong_tool_slots == 0
        and wrong_args == 0
        and missing_calls == 0
        and (extra_calls == 0 or allow_extra)
    )

    right_answer_wrong_tool = bool(final_ok and not tool_path_ok and wrong_tool_slots > 0)
    right_tool_wrong_args = bool(
        wrong_args > 0 and wrong_tool_slots == 0 and matched_tools == n_expected
    )
    has_extra = extra_calls > 0 and not allow_extra

    # Component scores in [0, 1]
    tool_score = 1.0 if n_expected == 0 else matched_tools / float(n_expected)
    args_score = 1.0
    if matched_tools:
        args_score = 1.0 - (wrong_args / float(matched_tools))
    elif n_expected:
        args_score = 0.0
    extra_penalty = 0.0 if (extra_calls == 0 or allow_extra) else min(1.0, extra_calls / float(max(1, n_expected)))
    answer_score = 1.0 if final_ok else 0.0

    overall = (
        0.35 * tool_score
        + 0.25 * args_score
        + 0.20 * (1.0 - extra_penalty)
        + 0.20 * answer_score
    )

    passed = tool_path_ok and final_ok

    return {
        "passed": passed,
        "overall": float(overall),
        "tool_score": float(tool_score),
        "args_score": float(args_score),
        "answer_score": float(answer_score),
        "n_expected": n_expected,
        "n_actual": n_actual,
        "matched_tools": matched_tools,
        "wrong_args": wrong_args,
        "wrong_tool_slots": wrong_tool_slots,
        "extra_calls": extra_calls,
        "missing_calls": missing_calls,
        "right_answer_wrong_tool": right_answer_wrong_tool,
        "right_tool_wrong_args": right_tool_wrong_args,
        "has_extra_calls": has_extra,
        "tool_path_ok": tool_path_ok,
    }
