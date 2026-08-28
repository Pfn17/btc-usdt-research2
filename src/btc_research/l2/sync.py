from __future__ import annotations

from dataclasses import dataclass

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.orderbook.book import OrderBook


@dataclass(frozen=True, slots=True)
class SyncResult:
    book: OrderBook
    applied_events: int
    skipped_events: int


class OrderBookSynchronizer:
    """Build a valid Binance Futures local book from REST + FIFO diffs."""

    def __init__(self, market_data: BinanceFuturesMarketData) -> None:
        self.market_data = market_data
        self.resync_count = 0

    def sync_snapshot(
        self,
        last_id: int,
        bids: list[PriceLevel],
        asks: list[PriceLevel],
        buffered: list[DepthUpdate],
    ) -> SyncResult:
        book = OrderBook.from_snapshot(last_id, bids, asks)
        target = last_id + 1
        start: int | None = None

        for index, event in enumerate(buffered):
            # Events fully before the snapshot cannot affect the rebuilt book.
            if event.final_update_id < target:
                continue

            # Binance Futures bootstrap bridge: U <= lastUpdateId+1 <= u.
            # Keep observation order; never sort the stream by update ID.
            if event.first_update_id <= target <= event.final_update_id:
                start = index
                break

            # The first relevant event starts after the required bridge. The
            # current snapshot is too old relative to the observed stream;
            # caller must obtain a newer snapshot while retaining the buffer.
            if event.first_update_id > target:
                raise RuntimeError(
                    f"snapshot behind buffered stream: target={target}, "
                    f"got {event.first_update_id}-{event.final_update_id} "
                    f"pu={event.previous_update_id}"
                )

        if start is None:
            raise RuntimeError(
                f"snapshot bridge not yet buffered: target={target}, "
                f"buffered_events={len(buffered)}"
            )

        applied = 0
        skipped = start
        for index, event in enumerate(buffered[start:], start=start):
            before = book.last_update_id
            try:
                book.apply(event, bootstrap=index == start)
            except ValueError as exc:
                raise RuntimeError(
                    f"depth sequence invalid at buffered event {index}: {exc}"
                ) from exc
            if book.last_update_id != before:
                applied += 1

        return SyncResult(book, applied, skipped)

    async def sync(self, buffered: list[DepthUpdate]) -> SyncResult:
        last_id, bids, asks = await self.market_data.snapshot()
        return self.sync_snapshot(last_id, bids, asks, buffered)
