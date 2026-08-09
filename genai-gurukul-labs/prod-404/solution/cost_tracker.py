"""PROD 404 — per-tenant token cost tracker (solution).

Offline teaching meter. Rates are didactic placeholders — verify live pricing
before any production spreadsheet (OpenAI/Anthropic rate cards change).
"""

from __future__ import annotations

from typing import Mapping


# Didactic blended rates USD per 1M tokens (input / output). Not live pricing.
DEFAULT_RATES_PER_M: dict[str, dict[str, float]] = {
    "gpt-demo": {"input": 2.50, "output": 10.00},
    "claude-demo": {"input": 3.00, "output": 15.00},
    "local-demo": {"input": 0.0, "output": 0.0},
}


class TenantCostTracker:
    """Accumulate token spend attributed by tenant_id (+ optional model)."""

    def __init__(
        self,
        rates_per_m: Mapping[str, Mapping[str, float]] | None = None,
        *,
        soft_budget_usd: float | None = None,
        hard_budget_usd: float | None = None,
    ) -> None:
        self.rates_per_m = {
            str(k): {"input": float(v["input"]), "output": float(v["output"])}
            for k, v in (rates_per_m or DEFAULT_RATES_PER_M).items()
        }
        if soft_budget_usd is not None and soft_budget_usd < 0:
            raise ValueError("soft_budget_usd must be >= 0")
        if hard_budget_usd is not None and hard_budget_usd < 0:
            raise ValueError("hard_budget_usd must be >= 0")
        if (
            soft_budget_usd is not None
            and hard_budget_usd is not None
            and soft_budget_usd > hard_budget_usd
        ):
            raise ValueError("soft_budget_usd cannot exceed hard_budget_usd")
        self.soft_budget_usd = soft_budget_usd
        self.hard_budget_usd = hard_budget_usd
        self._by_tenant: dict[str, dict[str, float | int]] = {}

    def record(
        self,
        tenant_id: str,
        *,
        model: str,
        tokens_in: int,
        tokens_out: int,
    ) -> dict[str, object]:
        """Record one LLM turn; return charge detail + tenant totals."""
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise TypeError("tenant_id must be a non-empty string")
        if tokens_in < 0 or tokens_out < 0:
            raise ValueError("token counts must be non-negative")
        if model not in self.rates_per_m:
            raise KeyError(f"unknown model rate card: {model}")

        rates = self.rates_per_m[model]
        usd = (tokens_in / 1_000_000.0) * rates["input"] + (
            tokens_out / 1_000_000.0
        ) * rates["output"]

        bucket = self._by_tenant.setdefault(
            tenant_id,
            {
                "tokens_in": 0,
                "tokens_out": 0,
                "usd": 0.0,
                "calls": 0,
            },
        )
        bucket["tokens_in"] = int(bucket["tokens_in"]) + tokens_in
        bucket["tokens_out"] = int(bucket["tokens_out"]) + tokens_out
        bucket["usd"] = float(bucket["usd"]) + usd
        bucket["calls"] = int(bucket["calls"]) + 1

        total = float(bucket["usd"])
        soft_hit = (
            self.soft_budget_usd is not None and total >= self.soft_budget_usd
        )
        hard_hit = (
            self.hard_budget_usd is not None and total >= self.hard_budget_usd
        )
        return {
            "tenant_id": tenant_id,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "usd_charge": round(usd, 8),
            "tenant_usd": round(total, 8),
            "soft_budget_hit": soft_hit,
            "hard_budget_hit": hard_hit,
        }

    def attribution(self) -> dict[str, dict[str, float | int]]:
        """Snapshot spend by tenant for Datadog/Splunk-style tags."""
        return {
            tid: {
                "tokens_in": int(b["tokens_in"]),
                "tokens_out": int(b["tokens_out"]),
                "usd": round(float(b["usd"]), 8),
                "calls": int(b["calls"]),
            }
            for tid, b in sorted(self._by_tenant.items())
        }

    def total_usd(self) -> float:
        return round(sum(float(b["usd"]) for b in self._by_tenant.values()), 8)
