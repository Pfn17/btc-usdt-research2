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
    """Build a valid local Binance Futures book from REST + buffered diffs.

    Futures differs from Spot: the first buffered event may overlap the
    snapshot at ``U <= lastUpdateId <= u`` or chain directly with ``pu ==
    lastUpdateId``. Subsequent events must preserve the ``pu == previous u``
    chain. Events remain in observation order and are never sorted by ID.
    """

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
        start: int | None = None

        for index, event in enumerate(buffered):
            # Binance Futures: drop events whose final update is strictly
            # before the snapshot ID. An event ending exactly at last_id may
            # be the bridge via pu == last_id and must not be discarded.
            if event.final_update_id < last_id:
                continue

            overlaps_snapshot = (
                event.first_update_id <= last_id <= event.final_update_id
            )
            chains_snapshot = event.previous_update_id == last_id
            if overlaps_snapshot or chains_snapshot:
                start = index
                break

            if event.first_update_id > last_id and event.previous_update_id != last_id:
                raise RuntimeError(
                    f"snapshot cannot be synchronized: expected overlap/pu with {last_id}, "
                    f"got {event.first_update_id}-{event.final_update_id} pu={event.previous_update_id}"
                )

        if start is None:
            raise RuntimeError("snapshot cannot be synchronized from buffered events")

        applied = 0
        skipped = start
        for index, event in enumerate(buffered[start:], start=start):
            before = book.last_update_id
            try:
                book.apply(event)
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
