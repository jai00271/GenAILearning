"""PROD 405 — TPM capacity planner (solution).

Didactic planner: tokens-per-minute demand vs provider headroom.
Verify live rate limits on provider dashboards — numbers here are teaching fixtures.
"""

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
    """Plan whether projected TPM fits under a fraction of the provider limit.

    ``safety_factor`` reserves headroom (default 0.8 → use at most 80% of limit).
    """
    if requests_per_minute < 0:
        raise ValueError("requests_per_minute must be >= 0")
    if avg_tokens_in < 0 or avg_tokens_out < 0:
        raise ValueError("avg token counts must be >= 0")
    if provider_tpm_limit <= 0:
        raise ValueError("provider_tpm_limit must be positive")
    if not (0.0 < safety_factor <= 1.0):
        raise ValueError("safety_factor must be in (0, 1]")

    tokens_per_request = avg_tokens_in + avg_tokens_out
    demand_tpm = requests_per_minute * tokens_per_request
    usable = provider_tpm_limit * safety_factor
    headroom = usable - demand_tpm
    utilization = demand_tpm / provider_tpm_limit if provider_tpm_limit else 0.0

    fits = demand_tpm <= usable
    # How many parallel "lanes" / shards if over budget
    shards_needed = 1
    if demand_tpm > 0 and usable > 0:
        import math

        shards_needed = max(1, int(math.ceil(demand_tpm / usable)))

    return {
        "fits": fits,
        "demand_tpm": float(demand_tpm),
        "usable_tpm": float(usable),
        "provider_tpm_limit": float(provider_tpm_limit),
        "safety_factor": float(safety_factor),
        "headroom_tpm": float(headroom),
        "utilization_of_limit": float(utilization),
        "tokens_per_request": float(tokens_per_request),
        "shards_needed": int(shards_needed),
        "recommendation": (
            "ok_within_headroom"
            if fits
            else "scale_out_or_raise_limit_or_reduce_tokens"
        ),
    }


def plan_tpm_from_mix(
    routes: Mapping[str, Mapping[str, float]],
    *,
    safety_factor: float = 0.8,
) -> dict[str, object]:
    """Plan per-provider when traffic is split across providers.

    ``routes`` maps provider → {rpm, avg_tokens_in, avg_tokens_out, tpm_limit}.
    """
    if not isinstance(routes, Mapping) or not routes:
        raise TypeError("routes must be a non-empty mapping")
    per: dict[str, dict[str, object]] = {}
    all_fit = True
    for name, cfg in routes.items():
        if not isinstance(cfg, Mapping):
            raise TypeError(f"route {name} must be a mapping")
        plan = plan_tpm(
            requests_per_minute=float(cfg["rpm"]),
            avg_tokens_in=float(cfg["avg_tokens_in"]),
            avg_tokens_out=float(cfg["avg_tokens_out"]),
            provider_tpm_limit=float(cfg["tpm_limit"]),
            safety_factor=safety_factor,
        )
        per[str(name)] = plan
        if not plan["fits"]:
            all_fit = False
    return {"fits_all": all_fit, "by_provider": per}
