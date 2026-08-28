import json
import time
from typing import Any

import httpx

from .types import DepthUpdate, PriceLevel


class BinanceFuturesMarketData:
    """Public Binance USDⓈ-M Futures market-data adapter."""

    def __init__(self, api_url: str, symbol: str = "BTCUSDT") -> None:
        self.api_url = api_url.rstrip("/")
        self.symbol = symbol.upper()

    async def snapshot(
        self, limit: int = 1000
    ) -> tuple[int, list[PriceLevel], list[PriceLevel]]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.api_url}/fapi/v1/depth",
                params={"symbol": self.symbol, "limit": limit},
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()

        bids = [PriceLevel(str(p), str(q)) for p, q in payload["bids"]]
        asks = [PriceLevel(str(p), str(q)) for p, q in payload["asks"]]
        return int(payload["lastUpdateId"]), bids, asks

    @staticmethod
    def decode_depth_message(message: str | bytes) -> DepthUpdate:
        """Decode a raw USDⓈ-M Futures depthUpdate event without losing payload bytes."""
        raw = message.encode() if isinstance(message, str) else message
        payload = json.loads(raw)

        if payload.get("e") != "depthUpdate":
            raise ValueError("unexpected Binance Futures event type")
        if "U" not in payload or "u" not in payload or "pu" not in payload:
            raise ValueError("Futures depthUpdate missing required sequence fields")

        return DepthUpdate(
            symbol=str(payload["s"]).upper(),
            event_time_ms=int(payload["E"]),
            transaction_time_ms=int(payload["T"]) if "T" in payload else None,
            receive_time_ns=time.time_ns(),
            first_update_id=int(payload["U"]),
            final_update_id=int(payload["u"]),
            previous_update_id=int(payload["pu"]),
            bids=[PriceLevel(str(p), str(q)) for p, q in payload.get("b", [])],
            asks=[PriceLevel(str(p), str(q)) for p, q in payload.get("a", [])],
            raw_event=raw,
        )
