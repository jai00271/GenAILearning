"""APP 301 — system prompt builder + few-shot message assembly (starter)."""

from __future__ import annotations


def build_system_prompt(
    role: str,
    constraints: list[str],
    output_contract: str | None = None,
) -> str:
    """Assemble a reviewable system prompt from role, constraints, optional contract.

    Sections (in order, blank-line separated):
      1) "Role: {role}"
      2) "Constraints:" followed by "- {item}" lines (skip section if constraints empty)
      3) "Output contract: {output_contract}" when provided and non-empty after strip

    Raises ValueError if role is empty/whitespace-only.
    Strip each constraint; skip blank constraint entries.
    """
    # TODO
    raise NotImplementedError


def few_shot_messages(
    system: str,
    examples: list[tuple[str, str]],
    user_query: str,
) -> list[dict[str, str]]:
    """Build chat messages: system + (user, assistant)* + final user.

    Each example is (user_content, assistant_content). Empty/whitespace system,
    example sides, or user_query raise ValueError.
    """
    # TODO
    raise NotImplementedError
