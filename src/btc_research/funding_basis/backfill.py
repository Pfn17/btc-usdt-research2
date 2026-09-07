from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time

from btc_research.marketdata.funding_basis import BinanceFuturesPremiumIndex
from btc_research.research.supabase import SupabaseResearchClient

log = logging.getLogger("btc_research.funding_basis.backfill")


async def backfill_funding_events(
    *,
    start_time_ms: int,
    symbol: str = "BTCUSDT",
    api_url: str = "https://fapi.binance.com",
    request_pause_seconds: float = 0.2,
    end_time_ms: int | None = None,
    market_data: BinanceFuturesPremiumIndex | None = None,
    supabase: SupabaseResearchClient | None = None,
) -> int:
    """Backfill completed funding events oldest-first using idempotent upserts.

    The function is deliberately bounded by the supplied start/end timestamps and
    does not modify any research rule. Re-running the same range is safe because
    ``funding_rate_events`` is upserted on ``symbol,funding_time_ms``.
    """
    if start_time_ms < 0:
        raise ValueError("start_time_ms must be non-negative")
    if end_time_ms is not None and end_time_ms <= start_time_ms:
        return 0

    owns_market_data = market_data is None
    owns_supabase = supabase is None
    market_data = market_data or BinanceFuturesPremiumIndex(api_url, symbol=symbol)
    if supabase is None:
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not supabase_url or not supabase_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        supabase = SupabaseResearchClient(supabase_url, supabase_key)

    cursor = start_time_ms
    end_ms = end_time_ms if end_time_ms is not None else int(time.time() * 1000)
    total = 0
    try:
        while cursor < end_ms:
            events = await market_data.funding_history(
                start_time_ms=cursor,
                end_time_ms=end_ms,
                limit=1000,
            )
            if not events:
                break

            ordered = sorted(events, key=lambda event: event.funding_time_ms)
            rows = [
                {
                    "symbol": event.symbol,
                    "funding_time_ms": event.funding_time_ms,
                    "funding_rate": event.funding_rate,
                    "mark_price": event.mark_price,
                }
                for event in ordered
                if event.symbol.upper() == symbol.upper()
                and cursor <= event.funding_time_ms <= end_ms
            ]
            if rows:
                supabase.upsert_funding_events(rows)
                total += len(rows)

            last_time = ordered[-1].funding_time_ms
            next_cursor = last_time + 1
            if next_cursor <= cursor:
                raise RuntimeError("funding backfill pagination did not advance")
            cursor = next_cursor
            log.info("funding backfill progress: events=%d next_cursor=%d", total, cursor)
            if cursor < end_ms and request_pause_seconds > 0:
                await asyncio.sleep(request_pause_seconds)
    finally:
        if owns_supabase:
            supabase.close()

    log.info("funding backfill complete: events=%d", total)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill Binance BTCUSDT funding-rate history")
    parser.add_argument("--start-ms", type=int, required=True, help="inclusive epoch milliseconds")
    parser.add_argument("--end-ms", type=int, default=None, help="exclusive operational bound; defaults to now")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--api-url", default="https://fapi.binance.com")
    parser.add_argument("--pause", type=float, default=0.2)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    asyncio.run(
        backfill_funding_events(
            start_time_ms=args.start_ms,
            end_time_ms=args.end_ms,
            symbol=args.symbol,
            api_url=args.api_url,
            request_pause_seconds=args.pause,
        )
    )


if __name__ == "__main__":
    main()
