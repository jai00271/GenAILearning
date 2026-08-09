"""PROD 404 — per-tenant token cost tracker (starter).

Fill in the TODOs. Success: GURUKUL_LAB=starter pytest prod-404/tests -q
"""

from __future__ import annotations

from typing import Mapping


DEFAULT_RATES_PER_M: dict[str, dict[str, float]] = {
    "gpt-demo": {"input": 2.50, "output": 10.00},
    "claude-demo": {"input": 3.00, "output": 15.00},
    "local-demo": {"input": 0.0, "output": 0.0},
}


class TenantCostTracker:
    def __init__(
        self,
        rates_per_m: Mapping[str, Mapping[str, float]] | None = None,
        *,
        soft_budget_usd: float | None = None,
        hard_budget_usd: float | None = None,
    ) -> None:
        # TODO: store rates + budgets; validate soft <= hard
        raise NotImplementedError("TODO: TenantCostTracker.__init__")

    def record(
        self,
        tenant_id: str,
        *,
        model: str,
        tokens_in: int,
        tokens_out: int,
    ) -> dict[str, object]:
        # TODO: charge from rate card; attribute to tenant; soft/hard flags
        raise NotImplementedError("TODO: record")

    def attribution(self) -> dict[str, dict[str, float | int]]:
        raise NotImplementedError("TODO: attribution")

    def total_usd(self) -> float:
        raise NotImplementedError("TODO: total_usd")
