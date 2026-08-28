from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from websockets.asyncio.client import ClientConnection, connect

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.types import DepthUpdate
from btc_research.orderbook.book import OrderBook

from .buffer import EventBuffer
from .sync import OrderBookSynchronizer

log = logging.getLogger(__name__)


class L2Collector:
    """Resilient Binance Futures depth collector with automatic book resync."""

    def __init__(self, market_data: BinanceFuturesMarketData, websocket_url: str, symbol: str = "BTCUSDT", buffer_size: int = 10_000, reconnect_min_s: float = 1.0, reconnect_max_s: float = 30.0) -> None:
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
        self._stop = asyncio.Event()

    @property
    def stream_url(self) -> str:
        return f"{self.websocket_url}/{self.symbol}@depth@100ms"

    def stop(self) -> None:
        self._stop.set()

    async def bootstrap(self) -> OrderBook:
        result = await self.syncer.sync(self.buffer.snapshot())
        self.book = result.book
        self.events_applied += result.applied_events
        self.resyncs += 1
        self.contaminated = False
        self.buffer.clear()
        return self.book

    async def _consume(self, ws: ClientConnection, on_update: Callable[[DepthUpdate], None] | None) -> None:
        async for message in ws:
            if self._stop.is_set():
                return
            event = self.market_data.decode_depth_message(message)
            self.events_received += 1
            self.buffer.append(event)
            if on_update:
                on_update(event)
            if self.book is None:
                continue
            try:
                before = self.book.last_update_id
                self.book.apply(event)
                if self.book.last_update_id != before:
                    self.events_applied += 1
            except ValueError:
                self.sequence_errors += 1
                self.contaminated = True
                await self.bootstrap()

    async def run(self, on_update: Callable[[DepthUpdate], None] | None = None) -> None:
        delay = self.reconnect_min_s
        while not self._stop.is_set():
            try:
                async with connect(self.stream_url, ping_interval=15, ping_timeout=10, close_timeout=5, max_queue=2048) as ws:
                    log.info("connected to %s", self.stream_url)
                    delay = self.reconnect_min_s
                    consumer = asyncio.create_task(self._consume(ws, on_update))
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
