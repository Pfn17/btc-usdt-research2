from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RateLimitMetrics:
    requests: int
    throttled_requests: int
    retries: int
    responses_429: int
    responses_418: int
    last_retry_after_s: float | None


class RestRateLimiter:
    """Small async pacing guard for public REST calls.

    It deliberately limits client-side request frequency without assuming a
    particular Binance weight schedule. Endpoint-specific weight accounting
    can be added later when the collector uses multiple weighted endpoints.
    """

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
        )
