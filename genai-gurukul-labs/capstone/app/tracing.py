"""Tracing stub — replace with OpenTelemetry / X-Ray / Datadog APM."""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator


def new_trace_id() -> str:
    return uuid.uuid4().hex


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Yield a mutable span dict; prints nothing by default (tests stay quiet)."""
    span: dict[str, Any] = {
        "name": name,
        "trace_id": new_trace_id(),
        "ts_start": time.time(),
        "attributes": dict(attributes or {}),
        "status": "ok",
    }
    try:
        yield span
    except Exception as exc:  # noqa: BLE001 — stub records then re-raises
        span["status"] = "error"
        span["error"] = type(exc).__name__
        raise
    finally:
        span["ts_end"] = time.time()
        span["duration_ms"] = (span["ts_end"] - span["ts_start"]) * 1000.0
