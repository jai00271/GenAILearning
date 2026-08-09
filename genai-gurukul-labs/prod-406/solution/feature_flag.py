"""PROD 406 — feature-flag percentage rollout + sticky hashing (solution).

Teaching stand-in for LaunchDarkly-style percentage rollouts with sticky bucketing.
Not a LaunchDarkly SDK.
"""

from __future__ import annotations

import hashlib
from typing import Mapping


def sticky_bucket(key: str, *, salt: str = "gurukul-prod-406", buckets: int = 100) -> int:
    """Map a sticky key (user/tenant/session) to bucket in [0, buckets)."""
    if not isinstance(key, str) or not key:
        raise TypeError("key must be a non-empty string")
    if buckets < 2:
        raise ValueError("buckets must be >= 2")
    digest = hashlib.sha256(f"{salt}:{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % buckets


def in_rollout(
    key: str,
    percentage: float,
    *,
    salt: str = "gurukul-prod-406",
    buckets: int = 100,
) -> bool:
    """True if sticky key falls in the first ``percentage``% of buckets.

    ``percentage`` is 0–100. Sticky: same key always gets the same decision for a
    fixed salt/percentage (monotonic expansion when percentage increases).
    """
    if percentage < 0 or percentage > 100:
        raise ValueError("percentage must be in [0, 100]")
    threshold = percentage  # with 100 buckets, bucket < percentage
    # For non-100 bucket counts, scale
    cut = (percentage / 100.0) * buckets
    return sticky_bucket(key, salt=salt, buckets=buckets) < cut


def choose_variant(
    key: str,
    flag: Mapping[str, object],
    *,
    salt: str | None = None,
) -> dict[str, object]:
    """Pick control vs treatment from a LaunchDarkly-shaped teaching flag.

    Expected ``flag`` keys:
      - ``key``: flag name
      - ``percentage``: 0–100 rollout to treatment
      - ``control``: control value (e.g. model or prompt version id)
      - ``treatment``: treatment value
      - optional ``salt`` override
    """
    if not isinstance(flag, Mapping):
        raise TypeError("flag must be a mapping")
    for req in ("key", "percentage", "control", "treatment"):
        if req not in flag:
            raise KeyError(f"flag missing {req}")
    use_salt = salt if salt is not None else str(flag.get("salt") or flag["key"])
    pct = float(flag["percentage"])
    on = in_rollout(key, pct, salt=use_salt)
    variant = "treatment" if on else "control"
    value = flag["treatment"] if on else flag["control"]
    return {
        "flag_key": str(flag["key"]),
        "sticky_key": key,
        "bucket": sticky_bucket(key, salt=use_salt),
        "percentage": pct,
        "variant": variant,
        "value": value,
        "in_rollout": on,
    }


def canary_plan(
    *,
    stages: list[float] | None = None,
    flag_key: str = "model_swap",
    control: str = "prompt-v1",
    treatment: str = "prompt-v2",
) -> list[dict[str, object]]:
    """Return a staged canary percentage plan (didactic default 1→5→25→100)."""
    pcts = stages if stages is not None else [1.0, 5.0, 25.0, 100.0]
    if not pcts:
        raise ValueError("stages must be non-empty")
    prev = -1.0
    plan: list[dict[str, object]] = []
    for i, p in enumerate(pcts):
        p = float(p)
        if p < 0 or p > 100:
            raise ValueError("stage percentages must be in [0, 100]")
        if p < prev:
            raise ValueError("stages must be non-decreasing")
        prev = p
        plan.append(
            {
                "stage": i + 1,
                "percentage": p,
                "flag": {
                    "key": flag_key,
                    "percentage": p,
                    "control": control,
                    "treatment": treatment,
                    "salt": flag_key,
                },
            }
        )
    return plan
