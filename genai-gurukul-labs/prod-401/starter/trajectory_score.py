"""PROD 401 — multi-step agent trajectory scoring (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-401/tests -q
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def _norm_args(args: Mapping[str, Any] | None) -> dict[str, Any]:
    if not args:
        return {}
    return {str(k): args[k] for k in sorted(args, key=lambda x: str(x))}


def score_trajectory(
    events: Sequence[Mapping[str, Any]],
    expected: Mapping[str, Any],
) -> dict[str, object]:
    """Score tool path + final answer. See solution for return schema."""
    # TODO: extract tool calls; compare to expected plan; set teaching flags:
    # right_answer_wrong_tool, right_tool_wrong_args, has_extra_calls
    raise NotImplementedError("TODO: score_trajectory")
