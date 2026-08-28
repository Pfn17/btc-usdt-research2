from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class RateLimitMetrics:
    requests: int
    throttled_requests: int
    retries: int
    responses_429: int
    responses_418: int
    last_retry_after_s: float | None
    last_used_weight_1m: int | None


class RestRateLimiter:
    """Async pacing and observability guard for public REST calls."""

    def __init__(self, min_interval_s: float = 0.25) -> None:
        if min_interval_s < 0:
            raise ValueError("min_interval_s must be >= 0")
        self.min_interval_s = min_interval_s
        self._lock = asyncio.Lock()
        self._next_allowed = 0.0
        self._requests = 0
        self._throttled = 0
        self._retries = 0
        self._responses_429 = 0
        self._responses_418 = 0
        self._last_retry_after: float | None = None
        self._last_used_weight_1m: int | None = None

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait_s = max(0.0, self._next_allowed - now)
            if wait_s:
                self._throttled += 1
                await asyncio.sleep(wait_s)
                now = time.monotonic()
            self._next_allowed = now + self.min_interval_s
            self._requests += 1

    def record_response(self, headers: Mapping[str, str]) -> None:
        """Record Binance's current IP request-weight header when present."""
        for name, value in headers.items():
            if name.lower() == "x-mbx-used-weight-1m":
                try:
                    self._last_used_weight_1m = int(value)
                except (TypeError, ValueError):
                    pass
                break

    def record_retry(self, status_code: int, retry_after_s: float | None) -> None:
        self._retries += 1
        if status_code == 429:
            self._responses_429 += 1
        elif status_code == 418:
            self._responses_418 += 1
        if retry_after_s is not None:
            self._last_retry_after = retry_after_s

    def metrics(self) -> RateLimitMetrics:
        return RateLimitMetrics(
            requests=self._requests,
            throttled_requests=self._throttled,
            retries=self._retries,
            responses_429=self._responses_429,
            responses_418=self._responses_418,
            last_retry_after_s=self._last_retry_after,
            last_used_weight_1m=self._last_used_weight_1m,
        )
