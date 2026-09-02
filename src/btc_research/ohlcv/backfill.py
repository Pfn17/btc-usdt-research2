from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time

from btc_research.marketdata.ohlcv import BinanceFuturesKlines
from btc_research.research.supabase import SupabaseResearchClient

log = logging.getLogger("btc_research.ohlcv.backfill")


async def backfill_ohlcv_1m(
    *,
    days: int = 90,
    symbol: str = "BTCUSDT",
    api_url: str = "https://fapi.binance.com",
    batch_size: int = 500,
    request_pause_seconds: float = 0.15,
) -> int:
    """Backfill closed 1m futures candles into Supabase, oldest first.

    This is intentionally a one-shot research utility. It does not touch the
    live L2 collector and only writes the idempotent ohlcv_1m primary key.
    """
    if days < 1 or days > 365:
        raise ValueError("days must be between 1 and 365")
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("batch_size must be between 1 and 1000")

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

    market_data = BinanceFuturesKlines(api_url, symbol=symbol)
    end_ms = (int(time.time() * 1000) // 60_000 - 1) * 60_000 + 59_999
    start_ms = end_ms - days * 24 * 60 * 60 * 1000 + 1
    total = 0

    with SupabaseResearchClient(supabase_url, supabase_key) as supabase:
        cursor = start_ms
        while cursor <= end_ms:
            rows = await market_data.historical(
                "1m",
                start_time_ms=cursor,
                end_time_ms=end_ms,
                limit=1000,
            )
            if not rows:
                break

            # Binance can return the currently forming candle at the boundary;
            # only persist candles whose close time is already in the past.
            closed = [row for row in rows if row.close_time_ms <= end_ms]
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
                for row in closed
            ]
            for offset in range(0, len(payload), batch_size):
                batch = payload[offset : offset + batch_size]
                supabase.upsert_ohlcv_1m(batch)
                total += len(batch)

            last_open = rows[-1].open_time_ms
            next_cursor = last_open + 60_000
            if next_cursor <= cursor:
                raise RuntimeError("OHLCV pagination did not advance")
            cursor = next_cursor
            log.info("backfill progress: %d candles, next=%d", total, cursor)
            if cursor <= end_ms and request_pause_seconds > 0:
                await asyncio.sleep(request_pause_seconds)

    log.info("OHLCV backfill complete: %d candles", total)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="One-shot Binance BTCUSDT 1m OHLCV backfill")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--api-url", default="https://fapi.binance.com")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--pause", type=float, default=0.15)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    asyncio.run(
        backfill_ohlcv_1m(
            days=args.days,
            symbol=args.symbol,
            api_url=args.api_url,
            batch_size=args.batch_size,
            request_pause_seconds=args.pause,
        )
    )


if __name__ == "__main__":
    main()
