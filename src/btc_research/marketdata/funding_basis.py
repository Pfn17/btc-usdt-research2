from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True, slots=True)
class BinancePremiumIndex:
    symbol: str
    mark_price: float
    index_price: float
    last_funding_rate: float
    next_funding_time_ms: int
    server_time_ms: int


class BinanceFuturesPremiumIndex:
    """Public Binance USD-M futures mark/index/funding adapter."""

    def __init__(self, api_url: str, symbol: str = "BTCUSDT") -> None:
        self.api_url = api_url.rstrip("/")
        self.symbol = symbol.upper()

    async def latest(self) -> BinancePremiumIndex:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.api_url}/fapi/v1/premiumIndex", params={"symbol": self.symbol})
            response.raise_for_status()
            row: dict[str, Any] = response.json()
        return BinancePremiumIndex(
            symbol=row["symbol"],
            mark_price=float(row["markPrice"]),
            index_price=float(row["indexPrice"]),
            last_funding_rate=float(row["lastFundingRate"]),
            next_funding_time_ms=int(row["nextFundingTime"]),
            server_time_ms=int(row["time"]),
        )
