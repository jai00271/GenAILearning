"""In-memory rate limit stub — swap for Redis / API Gateway usage plans."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class RateLimitStub:
    """Token-bucket style limiter keyed by API key (process-local only)."""

    max_per_minute: int = 30
    _hits: dict[str, list[float]] = field(default_factory=dict)

    def allow(self, key: str, now: float | None = None) -> bool:
        ts = now if now is not None else time.time()
        window_start = ts - 60.0
        bucket = [t for t in self._hits.get(key, []) if t >= window_start]
        if len(bucket) >= self.max_per_minute:
            self._hits[key] = bucket
            return False
        bucket.append(ts)
        self._hits[key] = bucket
        return True


limiter = RateLimitStub()
