from __future__ import annotations

from dataclasses import dataclass

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.types import DepthUpdate
from btc_research.orderbook.book import OrderBook


@dataclass(frozen=True, slots=True)
class SyncResult:
    book: OrderBook
    applied_events: int
    skipped_events: int


class OrderBookSynchronizer:
    """Builds a valid local book from buffered WebSocket events + REST snapshot.

    Binance depth synchronization requires buffering events before the snapshot,
    then starting with an event spanning ``lastUpdateId + 1``. After that, each
    event must be contiguous; a gap invalidates the book and triggers resync.
    """

    def __init__(self, market_data: BinanceFuturesMarketData) -> None:
        self.market_data = market_data
        self.resync_count = 0

    async def sync(self, buffered: list[DepthUpdate]) -> SyncResult:
        last_id, bids, asks = await self.market_data.snapshot()
        book = OrderBook.from_snapshot(last_id, bids, asks)
        events = sorted(
            (e for e in buffered if e.final_update_id > last_id),
            key=lambda e: (e.first_update_id, e.final_update_id),
        )

        start = None
        for index, event in enumerate(events):
            if event.first_update_id <= last_id + 1 <= event.final_update_id:
                start = index
                break
        if start is None:
            raise RuntimeError("snapshot cannot be synchronized from buffered events")

        applied = 0
        skipped = start
        for event in events[start:]:
            if event.first_update_id > book.last_update_id + 1:  # type: ignore[operator]
                raise RuntimeError(
                    f"depth gap during sync: expected {book.last_update_id + 1}, "
                    f"got {event.first_update_id}-{event.final_update_id}"
                )
            before = book.last_update_id
            book.apply(event)
            if book.last_update_id != before:
                applied += 1

        return SyncResult(book, applied, skipped)
