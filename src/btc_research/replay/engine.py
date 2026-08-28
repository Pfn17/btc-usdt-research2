from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.orderbook.book import OrderBook


@dataclass(frozen=True, slots=True)
class ReplayResult:
    events_seen: int
    events_applied: int
    sequence_errors: int
    final_update_id: int | None


class ReplayEngine:
    """Replay archived depth events into a deterministic local order book."""

    def __init__(self, snapshot_last_update_id: int, bids: list[PriceLevel], asks: list[PriceLevel]) -> None:
        self.book = OrderBook.from_snapshot(snapshot_last_update_id, bids, asks)

    def replay(self, events: Iterable[DepthUpdate], on_book: Callable[[OrderBook, DepthUpdate], None] | None = None) -> ReplayResult:
        seen = applied = errors = 0
        for event in events:
            seen += 1
            try:
                before = self.book.last_update_id
                self.book.apply(event)
                if self.book.last_update_id != before:
                    applied += 1
                    if on_book:
                        on_book(self.book, event)
            except ValueError:
                errors += 1
                raise
        return ReplayResult(seen, applied, errors, self.book.last_update_id)


def depth_update_from_archive_record(record) -> DepthUpdate:
    """Decode raw Binance JSON while preserving archived receive timestamp."""
    update = BinanceFuturesMarketData.decode_depth_message(record.raw_event)
    return DepthUpdate(
        symbol=update.symbol,
        event_time_ms=update.event_time_ms,
        receive_time_ns=record.receive_time_ns,
        first_update_id=update.first_update_id,
        final_update_id=update.final_update_id,
        bids=update.bids,
        asks=update.asks,
        raw_event=update.raw_event,
    )
