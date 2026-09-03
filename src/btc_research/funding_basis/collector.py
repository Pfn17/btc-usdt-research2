from __future__ import annotations

import asyncio
import logging
import time

from btc_research.marketdata.funding_basis import BinanceFuturesPremiumIndex
from btc_research.research.supabase import SupabaseResearchClient

log = logging.getLogger("btc_research.funding_basis")


async def collect_latest_funding_basis(market_data: BinanceFuturesPremiumIndex, supabase: SupabaseResearchClient, symbol: str) -> int:
    row = await market_data.latest()
    if row.symbol != symbol.upper():
        return 0
    payload = [{
        "symbol": row.symbol,
        "server_time_ms": row.server_time_ms,
        "mark_price": row.mark_price,
        "index_price": row.index_price,
        "last_funding_rate": row.last_funding_rate,
        "next_funding_time_ms": row.next_funding_time_ms,
    }]
    await asyncio.to_thread(supabase.upsert_funding_basis, payload)
    return 1


async def backfill_funding_events(
    market_data: BinanceFuturesPremiumIndex,
    supabase: SupabaseResearchClient,
    symbol: str,
    days: int = 90,
) -> int:
    """Backfill completed funding events once; idempotent by symbol/funding_time_ms."""
    days = max(1, min(days, 365))
    end_time_ms = int(time.time() * 1000)
    start_time_ms = end_time_ms - days * 86_400_000
    events = await market_data.funding_history(
        start_time_ms=start_time_ms,
        end_time_ms=end_time_ms,
        limit=1000,
    )
    rows = [
        {
            "symbol": event.symbol,
            "funding_time_ms": event.funding_time_ms,
            "funding_rate": event.funding_rate,
            "mark_price": event.mark_price,
        }
        for event in events
        if event.symbol.upper() == symbol.upper()
    ]
    if rows:
        await asyncio.to_thread(supabase.upsert_funding_events, rows)
    log.info("funding history backfill complete: days=%d events=%d", days, len(rows))
    return len(rows)
