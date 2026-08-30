from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone

from btc_research.archive.writer import ArchiveWriter
from btc_research.config import Settings
from btc_research.l2.collector import L2Collector
from btc_research.marketdata.binance import BinanceFuturesMarketData
from btc_research.research.supabase import SupabaseResearchClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("btc_research.worker")


async def main() -> None:
    settings = Settings()
    market_data = BinanceFuturesMarketData(
        settings.futures_api_url,
        symbol=settings.symbol,
    )
    archive = ArchiveWriter(settings.archive_dir)
    collector = L2Collector(
        market_data=market_data,
        websocket_url=settings.websocket_url,
        symbol=settings.symbol,
        buffer_size=10_000,
    )

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for the collector")

    supabase = SupabaseResearchClient(supabase_url, supabase_key)
    session_rows = supabase.insert_session(settings.symbol)
    if not session_rows or "id" not in session_rows[0]:
        supabase.close()
        raise RuntimeError("Supabase did not return a research session id")
    session_id = session_rows[0]["id"]

    def on_update(update) -> None:
        archive.append(update)

    async def health_loop() -> None:
        while True:
            try:
                last_update_id = collector.book.last_update_id if collector.book else None
                buffered = collector.buffer.snapshot()
                last_event_ms = buffered[-1].event_time_ms if buffered else None
                stale_after_ms = None
                latency_ms = None
                if last_event_ms is not None:
                    now_ms = time.time_ns() // 1_000_000
                    stale_after_ms = max(0, now_ms - last_event_ms)
                    latency_ms = stale_after_ms
                feed_status = "connected" if collector.events_received else "starting"
                if stale_after_ms is not None and stale_after_ms > 5_000:
                    feed_status = "stale"
                integrity_status = "contaminated" if collector.contaminated else "valid"
                supabase.insert_collector_health(session_id, {
                    "feed_status": feed_status,
                    "integrity_status": integrity_status,
                    "events_received": collector.events_received,
                    "events_applied": collector.events_applied,
                    "duplicate_events": 0,
                    "sequence_gaps": collector.sequence_errors,
                    "resync_count": collector.resyncs,
                    "last_update_id": last_update_id,
                    "stale_after_ms": stale_after_ms,
                    "latency_ms": latency_ms,
                    "contamination_active": collector.contaminated,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("failed to write collector health")
            await asyncio.sleep(30)

    health_task = asyncio.create_task(health_loop())
    log.info("starting BTCUSDT L2 collector for %s", settings.symbol)
    try:
        await collector.run(on_update=on_update)
    finally:
        health_task.cancel()
        await asyncio.gather(health_task, return_exceptions=True)
        collector.stop()
        supabase.close()


if __name__ == "__main__":
    asyncio.run(main())
