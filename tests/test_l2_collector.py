import asyncio
import json

import pytest

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.collector import (
    CollectorIntegrityError,
    CollectorState,
    FuturesL2Collector,
)


def event(first: int, final: int, previous: int) -> bytes:
    return json.dumps(
        {
            "e": "depthUpdate",
            "E": final,
            "T": final - 1,
            "s": "BTCUSDT",
            "U": first,
            "u": final,
            "pu": previous,
            "b": [["100", str(final)]],
            "a": [["101", "2"]],
        },
        separators=(",", ":"),
    ).encode()


class FakeWebSocket:
    def __init__(self, messages: list[bytes]) -> None:
        self.messages = asyncio.Queue()
        for message in messages:
            self.messages.put_nowait(message)

    async def recv(self) -> bytes:
        return await self.messages.get()


class FakeMarketData:
    def __init__(self, snapshot_id: int, delay_s: float = 0.01) -> None:
        self.snapshot_id = snapshot_id
        self.delay_s = delay_s
        self.decode_depth_message = BinanceFuturesMarketData.decode_depth_message

    async def snapshot(self, limit: int):
        await asyncio.sleep(self.delay_s)
        return self.snapshot_id, [], []


@pytest.mark.asyncio
async def test_synchronize_builds_book_from_snapshot_and_buffer():
    websocket = FakeWebSocket(
        [event(99, 101, 98), event(102, 103, 101)]
    )
    collector = FuturesL2Collector(
        market_data=FakeMarketData(100),
        websocket_url="wss://fstream.binance.com/public/ws",
    )

    await collector._synchronize(websocket, asyncio.Event())

    assert collector.state is CollectorState.VALID
    assert collector.book is not None
    assert collector.book.last_update_id == 103
    assert collector.metrics.accepted_events == 2


@pytest.mark.asyncio
async def test_synchronize_rejects_previous_id_mismatch():
    websocket = FakeWebSocket(
        [event(101, 102, 100), event(103, 104, 999)]
    )
    collector = FuturesL2Collector(
        market_data=FakeMarketData(100),
        websocket_url="wss://fstream.binance.com/public/ws",
    )

    with pytest.raises(CollectorIntegrityError, match="synchronization failed"):
        await collector._synchronize(websocket, asyncio.Event())

    assert collector.state is CollectorState.CONTAMINATED
    assert collector.metrics.previous_id_mismatches == 1


def test_stream_url_uses_futures_public_depth_stream():
    collector = FuturesL2Collector(
        market_data=FakeMarketData(100),
        websocket_url="wss://fstream.binance.com/public/ws",
        symbol="BTCUSDT",
    )
    assert collector.stream_url == (
        "wss://fstream.binance.com/public/ws/btcusdt@depth@100ms"
    )
