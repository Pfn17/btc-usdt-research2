from dataclasses import dataclass

import pytest

from btc_research.funding_basis.backfill import backfill_funding_events
from btc_research.marketdata.funding_basis import BinanceFundingEvent


@dataclass
class FakeMarketData:
    calls: list[tuple[int, int | None]]

    async def funding_history(self, *, start_time_ms: int, end_time_ms: int | None, limit: int):
        self.calls.append((start_time_ms, end_time_ms))
        if len(self.calls) == 1:
            return [
                BinanceFundingEvent("BTCUSDT", 100, 0.0001, 100.0),
                BinanceFundingEvent("BTCUSDT", 200, -0.0001, 101.0),
            ]
        return []


class FakeSupabase:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def upsert_funding_events(self, rows: list[dict]) -> None:
        self.rows.extend(rows)

    def close(self) -> None:
        raise AssertionError("injected client must not be closed by the function")


@pytest.mark.asyncio
async def test_funding_backfill_paginates_and_upserts() -> None:
    market = FakeMarketData([])
    supabase = FakeSupabase()

    total = await backfill_funding_events(
        start_time_ms=0,
        end_time_ms=300,
        market_data=market,
        supabase=supabase,
        request_pause_seconds=0,
    )

    assert total == 2
    assert [row["funding_time_ms"] for row in supabase.rows] == [100, 200]
    assert market.calls == [(0, 300), (201, 300)]


@pytest.mark.asyncio
async def test_funding_backfill_empty_range_is_noop() -> None:
    market = FakeMarketData([])
    supabase = FakeSupabase()

    total = await backfill_funding_events(
        start_time_ms=300,
        end_time_ms=300,
        market_data=market,
        supabase=supabase,
        request_pause_seconds=0,
    )

    assert total == 0
    assert market.calls == []
    assert supabase.rows == []
