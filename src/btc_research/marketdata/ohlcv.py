from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True, slots=True)
class BinanceKline:
    symbol: str
    interval: str
    open_time_ms: int
    close_time_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    trade_count: int
    taker_buy_volume: float
    taker_buy_quote_volume: float


class BinanceFuturesKlines:
    """Public Binance USD-M futures kline adapter. Read-only; no trading API."""

    def __init__(self, api_url: str, symbol: str = "BTCUSDT") -> None:
        self.api_url = api_url.rstrip("/")
        self.symbol = symbol.upper()

    @staticmethod
    def _parse_rows(symbol: str, interval: str, rows: list[list[Any]]) -> list[BinanceKline]:
        return [
            BinanceKline(
                symbol=symbol,
                interval=interval,
                open_time_ms=int(row[0]),
                close_time_ms=int(row[6]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                quote_volume=float(row[7]),
                trade_count=int(row[8]),
                taker_buy_volume=float(row[9]),
                taker_buy_quote_volume=float(row[10]),
            )
            for row in rows
        ]

    async def latest(self, interval: str = "1m", limit: int = 3) -> list[BinanceKline]:
        if interval != "1m":
            raise ValueError("only the preregistered 1m interval is supported")
        limit = max(1, min(int(limit), 1000))
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.api_url}/fapi/v1/klines",
                params={"symbol": self.symbol, "interval": interval, "limit": limit},
            )
            response.raise_for_status()
            rows: list[list[Any]] = response.json()
        return self._parse_rows(self.symbol, interval, rows)

    async def historical(
        self,
        interval: str = "1m",
        *,
        start_time_ms: int,
        end_time_ms: int,
        limit: int = 1000,
    ) -> list[BinanceKline]:
        """Fetch one bounded historical page using Binance start/end cursors."""
        if interval != "1m":
            raise ValueError("only the preregistered 1m interval is supported")
        if start_time_ms < 0 or end_time_ms < start_time_ms:
            raise ValueError("invalid historical time range")
        limit = max(1, min(int(limit), 1000))
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.api_url}/fapi/v1/klines",
                params={
                    "symbol": self.symbol,
                    "interval": interval,
                    "startTime": int(start_time_ms),
                    "endTime": int(end_time_ms),
                    "limit": limit,
                },
            )
            response.raise_for_status()
            rows: list[list[Any]] = response.json()
        return self._parse_rows(self.symbol, interval, rows)
