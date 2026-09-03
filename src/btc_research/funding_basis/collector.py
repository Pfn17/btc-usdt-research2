from __future__ import annotations

import logging

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
    await __import__("asyncio").to_thread(supabase.upsert_funding_basis, payload)
    return 1
