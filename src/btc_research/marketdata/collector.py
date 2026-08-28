from __future__ import annotations

import asyncio
import random
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Awaitable, Callable

import websockets
from websockets.exceptions import ConnectionClosed

from btc_research.integrity import IntegrityStatus, SequenceValidator
from btc_research.orderbook import OrderBook

from .archive import RawEventArchive
from .binance import BinanceFuturesMarketData
from .types import ContaminatedInterval, DepthUpdate


class CollectorState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    SYNCING = "SYNCING"
    VALID = "VALID"
    CONTAMINATED = "CONTAMINATED"
    STOPPED = "STOPPED"


@dataclass(slots=True)
class CollectorMetrics:
    received_events: int = 0
    accepted_events: int = 0
    duplicate_events: int = 0
    sequence_gaps: int = 0
    previous_id_mismatches: int = 0
    parse_errors: int = 0
    reconnects: int = 0
    resynchronizations: int = 0
    sync_failures: int = 0
    last_event_receive_time_ns: int | None = None
    last_event_time_ms: int | None = None
    last_update_id: int | None = None
    first_valid_receive_time_ns: int | None = None


OnValidUpdate = Callable[[OrderBook, DepthUpdate], Awaitable[None] | None]


class CollectorIntegrityError(RuntimeError):
    """Raised when a stream cannot be synchronized into a valid book."""


@dataclass(slots=True)
class FuturesL2Collector:
    """Execution-aware USDⓈ-M Futures diff-depth collector.

    The WebSocket is the primary event path. A REST snapshot is taken while
    events are buffered, then the buffer is applied only when the first event
    overlaps the snapshot and subsequent ``pu`` values match the last accepted
    ``u``. Any integrity break invalidates the book and forces a rebuild.
    """

    market_data: BinanceFuturesMarketData
    websocket_url: str
    symbol: str = "BTCUSDT"
    archive: RawEventArchive | None = None
    depth_limit: int = 1000
    max_buffered_events: int = 50_000
    reconnect_base_s: float = 0.5
    reconnect_max_s: float = 15.0
    on_valid_update: OnValidUpdate | None = None
    state: CollectorState = CollectorState.DISCONNECTED
    book: OrderBook | None = None
    metrics: CollectorMetrics = field(default_factory=CollectorMetrics)
    contaminated_intervals: list[ContaminatedInterval] = field(default_factory=list)
    _contamination_start_ms: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.symbol = self.symbol.upper()
        if self.depth_limit < 5:
            raise ValueError("depth_limit must be >= 5")
        if self.max_buffered_events < 1:
            raise ValueError("max_buffered_events must be >= 1")
        if not 0 <= self.reconnect_base_s <= self.reconnect_max_s:
            raise ValueError("invalid reconnect backoff bounds")

    @property
    def stream_url(self) -> str:
        base = self.websocket_url.rstrip("/")
        stream = f"{self.symbol.lower()}@depth@100ms"
        if base.endswith("/public/ws"):
            return f"{base}/{stream}"
        if base.endswith("/ws"):
            return f"{base}/{stream}"
        return f"{base}/public/ws/{stream}"

    async def run(self, stop_event: asyncio.Event) -> None:
        """Run until ``stop_event`` is set, reconnecting with bounded backoff."""
        backoff = self.reconnect_base_s
        while not stop_event.is_set():
            try:
                await self.run_session(stop_event)
                backoff = self.reconnect_base_s
            except asyncio.CancelledError:
                raise
            except Exception:
                self.state = CollectorState.DISCONNECTED
                self.metrics.reconnects += 1
                if stop_event.is_set():
                    break
                jitter = random.uniform(0.0, min(0.25, backoff * 0.25))
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=backoff + jitter)
                except asyncio.TimeoutError:
                    pass
                backoff = min(self.reconnect_max_s, max(self.reconnect_base_s, backoff * 2))
        self.state = CollectorState.STOPPED

    async def run_session(self, stop_event: asyncio.Event) -> None:
        """Run one WebSocket session; exceptions trigger an outer reconnect."""
        async with websockets.connect(
            self.stream_url,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=5,
            max_queue=None,
        ) as websocket:
            self.state = CollectorState.SYNCING
            await self._synchronize(websocket, stop_event)

            while not stop_event.is_set():
                try:
                    raw = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                except ConnectionClosed:
                    raise

                update = self._decode_and_archive(raw)
                if update.symbol != self.symbol:
                    continue
                self._record_received(update)

                validator = self._validator
                if validator is None or self.book is None:
                    raise CollectorIntegrityError("collector has no synchronized state")

                result = validator.accept(update)
                if result.status is IntegrityStatus.DUPLICATE:
                    self.metrics.duplicate_events += 1
                    continue
                if result.status is not IntegrityStatus.VALID:
                    self._record_integrity_failure(update, result.status)
                    self.metrics.resynchronizations += 1
                    self.state = CollectorState.SYNCING
                    await self._synchronize(websocket, stop_event)
                    continue

                self.book.apply(update)
                self._record_accepted(update)
                if self._contamination_start_ms is not None:
                    self._close_contamination(update.event_time_ms)
                self.state = CollectorState.VALID
                await self._emit(update)

    _validator: SequenceValidator | None = field(default=None, init=False, repr=False)

    async def _synchronize(self, websocket: object, stop_event: asyncio.Event) -> None:
        """Buffer WebSocket events while obtaining a fresh REST snapshot."""
        self.state = CollectorState.SYNCING
        buffer: deque[DepthUpdate] = deque()
        snapshot_task = asyncio.create_task(self.market_data.snapshot(self.depth_limit))
        try:
            while not snapshot_task.done() and not stop_event.is_set():
                try:
                    raw = await asyncio.wait_for(websocket.recv(), timeout=0.25)  # type: ignore[attr-defined]
                except asyncio.TimeoutError:
                    continue
                except ConnectionClosed:
                    raise
                update = self._decode_and_archive(raw)
                if update.symbol != self.symbol:
                    continue
                self._record_received(update)
                buffer.append(update)
                if len(buffer) > self.max_buffered_events:
                    raise CollectorIntegrityError("WebSocket buffer exceeded maximum during snapshot")

            if stop_event.is_set():
                return
            snapshot_id, bids, asks = await snapshot_task
            book = OrderBook.from_snapshot(snapshot_id, bids, asks)
            validator = SequenceValidator(snapshot_id)

            accepted_from_buffer: DepthUpdate | None = None
            for update in buffer:
                result = validator.accept(update)
                if result.status is IntegrityStatus.DUPLICATE:
                    self.metrics.duplicate_events += 1
                    continue
                if result.status is not IntegrityStatus.VALID:
                    self._record_integrity_failure(update, result.status)
                    self.metrics.sync_failures += 1
                    raise CollectorIntegrityError(
                        f"snapshot synchronization failed: {result.status.value}"
                    )
                book.apply(update)
                self._record_accepted(update)
                accepted_from_buffer = update

            self.book = book
            self._validator = validator
            self.metrics.last_update_id = book.last_update_id
            self.state = CollectorState.VALID
            if accepted_from_buffer is not None and self._contamination_start_ms is not None:
                self._close_contamination(accepted_from_buffer.event_time_ms)
            await self._emit(accepted_from_buffer)
        finally:
            if not snapshot_task.done():
                snapshot_task.cancel()
                try:
                    await snapshot_task
                except asyncio.CancelledError:
                    pass

    def _decode_and_archive(self, raw: str | bytes) -> DepthUpdate:
        raw_bytes = raw.encode() if isinstance(raw, str) else raw
        if self.archive is not None:
            self.archive.append(raw_bytes, time.time_ns())
        try:
            return self.market_data.decode_depth_message(raw_bytes)
        except Exception:
            self.metrics.parse_errors += 1
            raise

    def _record_received(self, update: DepthUpdate) -> None:
        self.metrics.received_events += 1
        self.metrics.last_event_receive_time_ns = update.receive_time_ns
        self.metrics.last_event_time_ms = update.event_time_ms
        if self.metrics.first_valid_receive_time_ns is None:
            self.metrics.first_valid_receive_time_ns = update.receive_time_ns

    def _record_accepted(self, update: DepthUpdate) -> None:
        self.metrics.accepted_events += 1
        self.metrics.last_update_id = update.final_update_id
        if self.book is not None:
            self.metrics.last_update_id = self.book.last_update_id

    def _record_integrity_failure(self, update: DepthUpdate, status: IntegrityStatus) -> None:
        if status is IntegrityStatus.GAP:
            self.metrics.sequence_gaps += 1
        elif status is IntegrityStatus.PREVIOUS_ID_MISMATCH:
            self.metrics.previous_id_mismatches += 1
        if self._contamination_start_ms is None:
            self._contamination_start_ms = update.event_time_ms
        self.state = CollectorState.CONTAMINATED
        self.book = None
        self._validator = None

    def _close_contamination(self, recovered_event_time_ms: int) -> None:
        if self._contamination_start_ms is None:
            return
        self.contaminated_intervals.append(
            ContaminatedInterval(
                start_ms=self._contamination_start_ms,
                end_ms=recovered_event_time_ms,
                reason="sequence_integrity_failure",
            )
        )
        self._contamination_start_ms = None

    async def _emit(self, update: DepthUpdate | None) -> None:
        if update is None or self.on_valid_update is None or self.book is None:
            return
        result = self.on_valid_update(self.book, update)
        if result is not None:
            await result
