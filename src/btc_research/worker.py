from __future__ import annotations

import asyncio
import logging

from btc_research.archive.writer import ArchiveWriter
from btc_research.config import Settings
from btc_research.l2.collector import L2Collector
from btc_research.marketdata.binance import BinanceFuturesMarketData

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

    def on_update(update) -> None:
        archive.append(update)

    log.info("starting BTCUSDT L2 collector for %s", settings.symbol)
    try:
        await collector.run(on_update=on_update)
    finally:
        collector.stop()


if __name__ == "__main__":
    asyncio.run(main())
