"""PROD 404 — retry storm detector (starter)."""

from __future__ import annotations

from typing import Sequence


def detect_retry_storm(
    events: Sequence[dict],
    *,
    window_s: float = 60.0,
    max_retries_in_window: int = 5,
    max_consecutive_failures: int = 3,
) -> dict[str, object]:
    # TODO: sliding-window retries + consecutive failure trip
    raise NotImplementedError("TODO: detect_retry_storm")
