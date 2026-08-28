from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx

from .rate_limit import RestRateLimiter
from .types import DepthUpdate, PriceLevel


class BinanceFuturesMarketData:
    """Public Binance USDⓈ-M Futures market-data adapter.

    REST snapshots are deliberately rate-limited and retried only for
    transient rate-limit/server responses. WebSocket depth remains the
    primary real-time path.
    """

    def __init__(
        self,
        api_url: str,
        symbol: str = "BTCUSDT",
        *,
        rest_min_interval_s: float = 0.25,
        max_snapshot_retries: int = 3,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.symbol = symbol.upper()
        if max_snapshot_retries < 0:
            raise ValueError("max_snapshot_retries must be >= 0")
        self.max_snapshot_retries = max_snapshot_retries
        self.rate_limiter = RestRateLimiter(rest_min_interval_s)
        self._snapshot_lock = asyncio.Lock()
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10)
            self._owns_client = True
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            return None

    async def snapshot(
        self, limit: int = 1000
    ) -> tuple[int, list[PriceLevel], list[PriceLevel]]:
        """Fetch one snapshot while preventing request bursts.

        Concurrent snapshot callers are serialized. A 429/418 response uses
        Retry-After when supplied, otherwise exponential backoff. 5xx
        responses receive the same transient retry treatment.
        """
        async with self._snapshot_lock:
            client = await self._get_client()
            last_error: Exception | None = None

            for attempt in range(self.max_snapshot_retries + 1):
                await self.rate_limiter.acquire()
                try:
                    response = await client.get(
                        f"{self.api_url}/fapi/v1/depth",
                        params={"symbol": self.symbol, "limit": limit},
                    )
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_error = exc
                    if attempt >= self.max_snapshot_retries:
                        raise
                    await asyncio.sleep(min(8.0, 0.5 * (2**attempt)))
                    continue

                if response.status_code in (429, 418) or response.status_code >= 500:
                    retry_after = self._retry_after(response)
                    self.rate_limiter.record_retry(response.status_code, retry_after)
                    last_error = httpx.HTTPStatusError(
                        f"Binance snapshot returned HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                    if attempt >= self.max_snapshot_retries:
                        raise last_error
                    delay = retry_after if retry_after is not None else min(
                        8.0, 0.5 * (2**attempt)
                    )
                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                payload: dict[str, Any] = response.json()
                bids = [PriceLevel(str(p), str(q)) for p, q in payload["bids"]]
                asks = [PriceLevel(str(p), str(q)) for p, q in payload["asks"]]
                return int(payload["lastUpdateId"]), bids, asks

            if last_error is not None:
                raise last_error
            raise RuntimeError("snapshot failed without an error")

    @staticmethod
    def decode_depth_message(message: str | bytes) -> DepthUpdate:
        """Decode a raw USDⓈ-M Futures depthUpdate event without losing payload bytes."""
        raw = message.encode() if isinstance(message, str) else message
        payload = json.loads(raw)

        if payload.get("e") != "depthUpdate":
            raise ValueError("unexpected Binance Futures event type")
        if "U" not in payload or "u" not in payload or "pu" not in payload:
            raise ValueError("Futures depthUpdate missing required sequence fields")

        return DepthUpdate(
            symbol=str(payload["s"]).upper(),
            event_time_ms=int(payload["E"]),
            transaction_time_ms=int(payload["T"]) if "T" in payload else None,
            receive_time_ns=time.time_ns(),
            first_update_id=int(payload["U"]),
            final_update_id=int(payload["u"]),
            previous_update_id=int(payload["pu"]),
            bids=[PriceLevel(str(p), str(q)) for p, q in payload.get("b", [])],
            asks=[PriceLevel(str(p), str(q)) for p, q in payload.get("a", [])],
            raw_event=raw,
        )
