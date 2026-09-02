from __future__ import annotations

import logging

from btc_research.marketdata.ohlcv import BinanceFuturesKlines
from btc_research.research.supabase import SupabaseResearchClient

log = logging.getLogger("btc_research.ohlcv")


async def collect_latest_ohlcv(
    market_data: BinanceFuturesKlines,
    supabase: SupabaseResearchClient,
    symbol: str,
) -> int:
    rows = await market_data.latest("1m", 3)
    payload = [
        {
            "symbol": row.symbol,
            "interval": row.interval,
            "open_time_ms": row.open_time_ms,
            "close_time_ms": row.close_time_ms,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
            "quote_volume": row.quote_volume,
            "trade_count": row.trade_count,
            "taker_buy_volume": row.taker_buy_volume,
            "taker_buy_quote_volume": row.taker_buy_quote_volume,
        }
        for row in rows
        if row.symbol == symbol.upper()
    ]
    if not payload:
        return 0
    supabase.upsert_ohlcv_1m(payload)
    return len(payload)
