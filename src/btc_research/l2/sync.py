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
    """Build a valid local book from buffered WebSocket events + REST snapshot.

    The buffer is treated as an observation-ordered FIFO. Events are never
    sorted by update ID because doing so would hide out-of-order delivery.
    Events before the first event spanning ``lastUpdateId + 1`` are skipped;
    every subsequent event must continue the sequence without a gap.
    """

    def __init__(self, market_data: BinanceFuturesMarketData) -> None:
        self.market_data = market_data
        self.resync_count = 0

    async def sync(self, buffered: list[DepthUpdate]) -> SyncResult:
        last_id, bids, asks = await self.market_data.snapshot()
        book = OrderBook.from_snapshot(last_id, bids, asks)

        start = None
        for index, event in enumerate(buffered):
            if event.final_update_id <= last_id:
                continue
            if event.first_update_id <= last_id + 1 <= event.final_update_id:
                start = index
                break
            if event.first_update_id > last_id + 1:
                # The required bridge event has already been missed in the
                # observation stream; do not sort later events into existence.
                raise RuntimeError(
                    f"snapshot cannot be synchronized: expected event spanning {last_id + 1}, "
                    f"got {event.first_update_id}-{event.final_update_id}"
                )

        if start is None:
            raise RuntimeError("snapshot cannot be synchronized from buffered events")

        applied = 0
        skipped = start
        for event in buffered[start:]:
            if event.first_update_id > book.last_update_id + 1:
                raise RuntimeError(
                    f"depth gap during sync: expected {book.last_update_id + 1}, "
                    f"got {event.first_update_id}-{event.final_update_id}"
                )
            before = book.last_update_id
            book.apply(event)
            if book.last_update_id != before:
                applied += 1

        return SyncResult(book, applied, skipped)
