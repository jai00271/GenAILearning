"""PROD 404 — retry storm detector (solution).

Detects bursty retries that amplify provider load and cost (429/5xx storms).
"""

from __future__ import annotations

from typing import Sequence


def detect_retry_storm(
    events: Sequence[dict],
    *,
    window_s: float = 60.0,
    max_retries_in_window: int = 5,
    max_consecutive_failures: int = 3,
) -> dict[str, object]:
    """Analyze retry/failure events for storm signals.

    Each event is a mapping with at least:
      - ``t``: float timestamp (seconds, monotonic-ish)
      - ``kind``: ``"retry"`` | ``"failure"`` | ``"success"`` | other
      - optional ``status``: HTTP-ish code (429, 500, …)
      - optional ``provider``: string tag for attribution

    Returns flagged=True when either:
      - retries in any sliding window of ``window_s`` exceed ``max_retries_in_window``, or
      - consecutive failures (retry or failure kinds) reach ``max_consecutive_failures``.
    """
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise TypeError("events must be a sequence of mappings")
    if window_s <= 0:
        raise ValueError("window_s must be positive")
    if max_retries_in_window < 1:
        raise ValueError("max_retries_in_window must be >= 1")
    if max_consecutive_failures < 1:
        raise ValueError("max_consecutive_failures must be >= 1")

    for i, ev in enumerate(events):
        if not isinstance(ev, dict):
            raise TypeError(f"event {i} must be a dict")
        if "t" not in ev:
            raise ValueError(f"event {i} missing t")

    retry_times = sorted(
        float(ev["t"]) for ev in events if str(ev.get("kind", "")).lower() == "retry"
    )

    window_hits: list[dict[str, object]] = []
    peak = 0
    for i, t0 in enumerate(retry_times):
        # Count retries in [t0, t0 + window_s]
        count = 0
        for t1 in retry_times[i:]:
            if t1 - t0 <= window_s:
                count += 1
            else:
                break
        peak = max(peak, count)
        if count > max_retries_in_window:
            window_hits.append(
                {
                    "window_start": t0,
                    "window_end": t0 + window_s,
                    "retries": count,
                }
            )

    consecutive = 0
    max_consec = 0
    consec_trip_at: int | None = None
    for i, ev in enumerate(events):
        kind = str(ev.get("kind", "")).lower()
        status = ev.get("status")
        is_fail = kind in {"retry", "failure"} or (
            isinstance(status, int) and status >= 400
        )
        if kind == "success":
            consecutive = 0
            continue
        if is_fail:
            consecutive += 1
            max_consec = max(max_consec, consecutive)
            if consecutive >= max_consecutive_failures and consec_trip_at is None:
                consec_trip_at = i
        else:
            consecutive = 0

    storm_window = len(window_hits) > 0
    storm_consec = max_consec >= max_consecutive_failures
    reasons: list[str] = []
    if storm_window:
        reasons.append("retries_in_window")
    if storm_consec:
        reasons.append("consecutive_failures")

    # Provider attribution for ops dashboards
    by_provider: dict[str, int] = {}
    for ev in events:
        if str(ev.get("kind", "")).lower() == "retry":
            p = str(ev.get("provider") or "unknown")
            by_provider[p] = by_provider.get(p, 0) + 1

    return {
        "flagged": bool(reasons),
        "reasons": reasons,
        "peak_retries_in_window": peak,
        "window_hits": window_hits,
        "max_consecutive_failures": max_consec,
        "consecutive_trip_index": consec_trip_at,
        "retry_count": len(retry_times),
        "by_provider": by_provider,
        "window_s": float(window_s),
        "max_retries_in_window": int(max_retries_in_window),
    }
