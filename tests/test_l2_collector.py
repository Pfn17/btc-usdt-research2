import pytest

from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.orderbook.book import OrderBook
from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.l2 import EventBuffer, OrderBookSynchronizer


def event(u: int, U: int | None = None) -> DepthUpdate:
    first = u if U is None else U
    return DepthUpdate("BTCUSDT", 1_000, 1, first, u, [PriceLevel("100", "1")], [PriceLevel("101", "2")], b"{}")


def test_buffer_is_bounded_and_counts_drops() -> None:
    buf = EventBuffer(2)
    buf.append(event(1))
    buf.append(event(2))
    buf.append(event(3))
    assert len(buf) == 2
    assert buf.dropped == 1
    assert [x.final_update_id for x in buf.snapshot()] == [2, 3]


def test_sync_starts_with_event_spanning_snapshot_plus_one() -> None:
    class Adapter:
        async def snapshot(self):
            return 10, [PriceLevel("100", "1")], [PriceLevel("101", "2")]

    async def run():
        result = await OrderBookSynchronizer(Adapter()).sync([event(10), event(12, 11), event(13)])
        assert result.book.last_update_id == 13
        assert result.applied_events == 2
        assert result.book.bids

    import asyncio
    asyncio.run(run())


def test_orderbook_rejects_sequence_gap() -> None:
    book = OrderBook.from_snapshot(10, [PriceLevel("100", "1")], [PriceLevel("101", "2")])
    with pytest.raises(ValueError, match="sequence gap"):
        book.apply(event(12, 12))


def test_binance_stream_url() -> None:
    adapter = BinanceFuturesMarketData("https://fapi.binance.com")
    from btc_research.l2 import L2Collector
    collector = L2Collector(adapter, "wss://fstream.binance.com/ws", "BTCUSDT")
    assert collector.stream_url == "wss://fstream.binance.com/ws/btcusdt@depth@100ms"
