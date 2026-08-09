"""PROD 405 — TPM capacity planner (starter)."""

from __future__ import annotations

from typing import Mapping


def plan_tpm(
    *,
    requests_per_minute: float,
    avg_tokens_in: float,
    avg_tokens_out: float,
    provider_tpm_limit: float,
    safety_factor: float = 0.8,
) -> dict[str, object]:
    # TODO: demand_tpm vs usable headroom; shards_needed
    raise NotImplementedError("TODO: plan_tpm")


def plan_tpm_from_mix(
    routes: Mapping[str, Mapping[str, float]],
    *,
    safety_factor: float = 0.8,
) -> dict[str, object]:
    raise NotImplementedError("TODO: plan_tpm_from_mix")
