"""APP 301 — system prompt builder + few-shot message assembly (solution)."""

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
    """
    cleaned_role = role.strip()
    if not cleaned_role:
        raise ValueError("role must be non-empty")

    parts: list[str] = [f"Role: {cleaned_role}"]

    cleaned_constraints = [c.strip() for c in constraints if c.strip()]
    if cleaned_constraints:
        lines = ["Constraints:"] + [f"- {c}" for c in cleaned_constraints]
        parts.append("\n".join(lines))

    if output_contract is not None:
        contract = output_contract.strip()
        if contract:
            parts.append(f"Output contract: {contract}")

    return "\n\n".join(parts)


def few_shot_messages(
    system: str,
    examples: list[tuple[str, str]],
    user_query: str,
) -> list[dict[str, str]]:
    """Build chat messages: system + (user, assistant)* + final user.

    Each example is (user_content, assistant_content). Empty/whitespace system,
    example sides, or user_query raise ValueError.
    """
    cleaned_system = system.strip()
    if not cleaned_system:
        raise ValueError("system must be non-empty")
    cleaned_query = user_query.strip()
    if not cleaned_query:
        raise ValueError("user_query must be non-empty")

    messages: list[dict[str, str]] = [{"role": "system", "content": cleaned_system}]
    for i, pair in enumerate(examples):
        if len(pair) != 2:
            raise ValueError(f"example {i} must be a (user, assistant) pair")
        user_ex, asst_ex = pair[0].strip(), pair[1].strip()
        if not user_ex or not asst_ex:
            raise ValueError(f"example {i} sides must be non-empty")
        messages.append({"role": "user", "content": user_ex})
        messages.append({"role": "assistant", "content": asst_ex})
    messages.append({"role": "user", "content": cleaned_query})
    return messages
