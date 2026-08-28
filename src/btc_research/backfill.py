from __future__ import annotations

import asyncio
from pathlib import Path

from btc_research.archive.reader import ArchiveReader
from btc_research.archive.writer import ArchiveWriter
from btc_research.marketdata.binance import BinanceFuturesMarketData


async def backfill_snapshot(symbol: str = "BTCUSDT", api_url: str = "https://fapi.binance.com", output_dir: str = "./data/snapshots", limit: int = 1000) -> Path:
    """Fetch and persist a timestamped REST snapshot for rebuild/recovery."""
    adapter = BinanceFuturesMarketData(api_url, symbol)
    last_id, bids, asks = await adapter.snapshot(limit)
    out = Path(output_dir) / symbol.upper()
    out.mkdir(parents=True, exist_ok=True)
    import json, time
    path = out / f"snapshot-{int(time.time() * 1000)}.json"
    payload = {
        "symbol": symbol.upper(), "snapshot_time_ms": int(time.time() * 1000),
        "last_update_id": last_id,
        "bids": [[x.price, x.quantity] for x in bids],
        "asks": [[x.price, x.quantity] for x in asks],
    }
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    return path
