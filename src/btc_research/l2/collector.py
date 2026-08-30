from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

import httpx
from websockets.asyncio.client import ClientConnection, connect

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.types import DepthUpdate
from btc_research.orderbook.book import OrderBook

from .buffer import EventBuffer
from .sync import OrderBookSynchronizer

log = logging.getLogger(__name__)


class L2Collector:
    """Resilient Binance Futures depth collector with automatic book resync."""

    def __init__(self, market_data: BinanceFuturesMarketData, websocket_url: str, symbol: str = "BTCUSDT", buffer_size: int = 10_000, reconnect_min_s: float = 2.0, reconnect_max_s: float = 60.0) -> None:
        self.market_data = market_data
        self.websocket_url = websocket_url.rstrip("/")
        self.symbol = symbol.lower()
        self.buffer = EventBuffer(buffer_size)
        self.syncer = OrderBookSynchronizer(market_data)
        self.reconnect_min_s = reconnect_min_s
        self.reconnect_max_s = reconnect_max_s
        self.book: OrderBook | None = None
        self.contaminated = True
        self.resyncs = 0
        self.events_received = 0
        self.events_applied = 0
        self.sequence_errors = 0
        self._bootstrapping = False
        self._stop = asyncio.Event()

    @property
    def stream_url(self) -> str:
        return f"{self.websocket_url}/{self.symbol}@depth@100ms"

    def stop(self) -> None:
        self._stop.set()

    async def _wait_for_buffer_progress(self, previous_len: int, timeout_s: float = 2.0) -> None:
        deadline = asyncio.get_running_loop().time() + timeout_s
        while len(self.buffer) <= previous_len and not self._stop.is_set():
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return
            await asyncio.sleep(min(0.05, remaining))

    @staticmethod
    def _retry_after_seconds(exc: httpx.HTTPStatusError) -> float | None:
        value = exc.response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            return None

    async def bootstrap(self) -> OrderBook:
        """Build a synchronized book while preserving the live FIFO buffer."""
        self._bootstrapping = True
        delay = self.reconnect_min_s
        try:
            for attempt in range(1, 21):
                try:
                    last_id, bids, asks = await self.market_data.snapshot()
                except httpx.HTTPStatusError as exc:
                    retry_after = self._retry_after_seconds(exc)
                    if exc.response.status_code in (418, 429):
                        wait_s = retry_after if retry_after is not None else min(delay, self.reconnect_max_s)
                        log.error("Binance snapshot returned HTTP %d; backing off %.1fs", exc.response.status_code, wait_s)
                        if attempt == 20:
                            raise
                        try:
                            await asyncio.wait_for(self._stop.wait(), timeout=wait_s)
                        except asyncio.TimeoutError:
                            pass
                        delay = min(max(delay * 2, self.reconnect_min_s), self.reconnect_max_s)
                        continue
                    raise

                buffered = self.buffer.snapshot()
                target = last_id + 1
                latest_u = buffered[-1].final_update_id if buffered else None
                if latest_u is None or latest_u < target:
                    await self._wait_for_buffer_progress(len(buffered), timeout_s=1.0)
                    buffered = self.buffer.snapshot()

                try:
                    result = self.syncer.sync_snapshot(last_id, bids, asks, buffered)
                except RuntimeError as exc:
                    log.warning(
                        "snapshot synchronization unavailable (attempt %d/20): %s; waiting for stream alignment",
                        attempt,
                        exc,
                    )
                    if attempt == 20:
                        raise
                    await asyncio.sleep(0.1)
                    continue

                self.buffer.swap()
                self.book = result.book
                self.events_applied += result.applied_events
                self.resyncs += 1
                self.contaminated = False
                log.info(
                    "snapshot synchronized: last_update_id=%d applied_events=%d skipped_events=%d",
                    self.book.last_update_id,
                    result.applied_events,
                    result.skipped_events,
                )
                return self.book

            raise RuntimeError("snapshot bootstrap exhausted retries")
        finally:
            self._bootstrapping = False

    async def _consume(
        self,
        ws: ClientConnection,
        on_update: Callable[[DepthUpdate], None] | None,
        on_raw: Callable[[DepthUpdate], None] | None,
    ) -> None:
        async for message in ws:
            if self._stop.is_set():
                return
            event = self.market_data.decode_depth_message(message)
            self.events_received += 1
            self.buffer.append(event)
            if on_raw:
                on_raw(event)

            if self.book is None or self._bootstrapping:
                continue
            try:
                before = self.book.last_update_id
                self.book.apply(event)
                if self.book.last_update_id != before:
                    self.events_applied += 1
                    if on_update:
                        on_update(event)
            except ValueError:
                self.sequence_errors += 1
                self.contaminated = True
                await self.bootstrap()

    async def run(
        self,
        on_update: Callable[[DepthUpdate], None] | None = None,
        on_raw: Callable[[DepthUpdate], None] | None = None,
    ) -> None:
        delay = self.reconnect_min_s
        while not self._stop.is_set():
            try:
                async with connect(self.stream_url, ping_interval=15, ping_timeout=10, close_timeout=5, max_queue=2048) as ws:
                    log.info("connected to %s", self.stream_url)
                    delay = self.reconnect_min_s
                    consumer = asyncio.create_task(self._consume(ws, on_update, on_raw))
                    try:
                        await asyncio.sleep(0)
                        await self.bootstrap()
                        await consumer
                    finally:
                        if not consumer.done():
                            consumer.cancel()
                            await asyncio.gather(consumer, return_exceptions=True)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.contaminated = True
                if self._stop.is_set():
                    break
                log.exception("collector connection failed; reconnecting in %.1fs", delay)
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
                delay = min(delay * 2, self.reconnect_max_s)
