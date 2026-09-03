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


@dataclass(frozen=True, slots=True)
class BinanceFundingEvent:
    symbol: str
    funding_time_ms: int
    funding_rate: float
    mark_price: float


class BinanceFuturesPremiumIndex:
    """Public Binance USD-M futures mark/index/funding adapter."""

    def __init__(self, api_url: str, symbol: str = "BTCUSDT") -> None:
        self.api_url = api_url.rstrip("/")
        self.symbol = symbol.upper()

    async def latest(self) -> BinancePremiumIndex:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.api_url}/fapi/v1/premiumIndex",
                params={"symbol": self.symbol},
            )
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

    async def funding_history(
        self,
        *,
        start_time_ms: int,
        end_time_ms: int | None = None,
        limit: int = 1000,
    ) -> list[BinanceFundingEvent]:
        """Fetch completed funding events from the public historical endpoint."""
        params: dict[str, Any] = {
            "symbol": self.symbol,
            "startTime": start_time_ms,
            "limit": min(max(limit, 1), 1000),
        }
        if end_time_ms is not None:
            params["endTime"] = end_time_ms
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.api_url}/fapi/v1/fundingRate", params=params)
            response.raise_for_status()
            rows: list[dict[str, Any]] = response.json()
        return [
            BinanceFundingEvent(
                symbol=row["symbol"],
                funding_time_ms=int(row["fundingTime"]),
                funding_rate=float(row["fundingRate"]),
                mark_price=float(row["markPrice"]),
            )
            for row in rows
            if row["symbol"].upper() == self.symbol
        ]
