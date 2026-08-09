"""PROD 406 — feature-flag percentage rollout + sticky hashing (starter)."""

from __future__ import annotations

from typing import Mapping


def sticky_bucket(key: str, *, salt: str = "gurukul-prod-406", buckets: int = 100) -> int:
    # TODO: stable hash → bucket in [0, buckets)
    raise NotImplementedError("TODO: sticky_bucket")


def in_rollout(
    key: str,
    percentage: float,
    *,
    salt: str = "gurukul-prod-406",
    buckets: int = 100,
) -> bool:
    raise NotImplementedError("TODO: in_rollout")


def choose_variant(
    key: str,
    flag: Mapping[str, object],
    *,
    salt: str | None = None,
) -> dict[str, object]:
    raise NotImplementedError("TODO: choose_variant")


def canary_plan(
    *,
    stages: list[float] | None = None,
    flag_key: str = "model_swap",
    control: str = "prompt-v1",
    treatment: str = "prompt-v2",
) -> list[dict[str, object]]:
    raise NotImplementedError("TODO: canary_plan")
