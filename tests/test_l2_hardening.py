import asyncio
from unittest.mock import patch

from btc_research.l2 import EventBuffer, L2Collector, OrderBookSynchronizer
from btc_research.marketdata.types import DepthUpdate, PriceLevel


def event(first: int, final: int | None = None, previous: int | None = None) -> DepthUpdate:
    final = first if final is None else final
    if previous is None:
        previous = first - 1
    return DepthUpdate(
        "BTCUSDT",
        1_000 + final,
        2_000 + final,
        first,
        final,
        [PriceLevel("100", "1")],
        [PriceLevel("101", "1")],
        b"{}",
        previous,
    )


def test_buffer_swap_preserves_fifo_and_detaches_queue() -> None:
    buffer = EventBuffer(4)
    buffer.append(event(101))
    buffer.append(event(102))
    detached = buffer.swap()
    buffer.append(event(103))
    assert [item.final_update_id for item in detached] == [101, 102]
    assert [item.final_update_id for item in buffer.snapshot()] == [103]


def test_sync_rejects_missing_bridge_without_sorting() -> None:
    class Adapter:
        async def snapshot(self):
            return 100, [PriceLevel("100", "1")], [PriceLevel("101", "1")]

    async def run() -> None:
        synchronizer = OrderBookSynchronizer(Adapter())
        try:
            await synchronizer.sync([event(102), event(101)])
        except RuntimeError as exc:
            assert "snapshot behind buffered stream" in str(exc)
        else:
            raise AssertionError("out-of-order buffer must not be sorted into a valid sync")

    asyncio.run(run())


def test_sync_accepts_futures_pu_bridge() -> None:
    class Adapter:
        async def snapshot(self):
            return 100, [PriceLevel("100", "1")], [PriceLevel("101", "1")]

    async def run() -> None:
        synchronizer = OrderBookSynchronizer(Adapter())
        result = await synchronizer.sync([event(101), event(102)])
        assert result.book.last_update_id == 102
        assert result.applied_events == 2

    asyncio.run(run())


def test_collector_keeps_events_arriving_during_snapshot() -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    class Adapter:
        async def snapshot(self):
            started.set()
            await release.wait()
            return 100, [PriceLevel("100", "1")], [PriceLevel("101", "1")]

    async def run() -> None:
        collector = L2Collector(Adapter(), "wss://example.test/ws")
        collector.buffer.append(event(101))
        task = asyncio.create_task(collector.bootstrap())
        await started.wait()
        collector.buffer.append(event(102))
        release.set()
        book = await task
        assert book.last_update_id == 102
        assert len(collector.buffer) == 0
        assert collector.contaminated is False

    asyncio.run(run())


def test_alignment_retry_uses_bounded_exponential_backoff() -> None:
    class Adapter:
        async def snapshot(self):
            return 100, [PriceLevel("100", "1")], [PriceLevel("101", "1")]

    class FlakySynchronizer:
        def __init__(self):
            self.calls = 0

        def sync_snapshot(self, last_id, bids, asks, buffered):
            self.calls += 1
            if self.calls < 3:
                raise RuntimeError("snapshot behind buffered stream")
            book = __import__("btc_research.orderbook.book", fromlist=["OrderBook"]).OrderBook.from_snapshot(last_id, bids, asks)
            return type("Result", (), {"book": book, "applied_events": 0, "skipped_events": 0})()

    async def run() -> None:
        collector = L2Collector(Adapter(), "wss://example.test/ws")
        collector.syncer = FlakySynchronizer()
        waits: list[float] = []

        async def fake_wait_for(awaitable, timeout):
            waits.append(timeout)
            awaitable.close()
            raise asyncio.TimeoutError

        with patch("btc_research.l2.collector.asyncio.wait_for", side_effect=fake_wait_for):
            book = await collector.bootstrap()

        assert book.last_update_id == 100
        assert len(waits) == 2
        assert waits[0] >= 0.25
        assert waits[1] >= 0.50
        assert waits[1] > waits[0]

    asyncio.run(run())
