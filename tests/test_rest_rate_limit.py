import asyncio

import httpx
import pytest

from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.marketdata.rate_limit import RestRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_tracks_throttling() -> None:
    limiter = RestRateLimiter(min_interval_s=0)
    await limiter.acquire()
    await limiter.acquire()

    metrics = limiter.metrics()
    assert metrics.requests == 2
    assert metrics.throttled_requests == 0


@pytest.mark.asyncio
async def test_snapshot_retries_429_using_retry_after() -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, request=request)
        return httpx.Response(
            200,
            json={
                "lastUpdateId": 42,
                "bids": [["100.0", "1.0"]],
                "asks": [["101.0", "2.0"]],
            },
            request=request,
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = BinanceFuturesMarketData(
        "https://example.test",
        rest_min_interval_s=0,
        client=client,
    )

    try:
        update_id, bids, asks = await adapter.snapshot()
    finally:
        await client.aclose()

    assert update_id == 42
    assert bids[0].price == "100.0"
    assert asks[0].quantity == "2.0"
    metrics = adapter.rate_limiter.metrics()
    assert metrics.responses_429 == 1
    assert metrics.retries == 1
    assert calls == 2


@pytest.mark.asyncio
async def test_concurrent_snapshots_are_serialized() -> None:
    active = 0
    maximum = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        await asyncio.sleep(0)
        active -= 1
        return httpx.Response(
            200,
            json={"lastUpdateId": 1, "bids": [], "asks": []},
            request=request,
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = BinanceFuturesMarketData(
        "https://example.test", rest_min_interval_s=0, client=client
    )

    try:
        await asyncio.gather(adapter.snapshot(), adapter.snapshot(), adapter.snapshot())
    finally:
        await client.aclose()

    assert maximum == 1
