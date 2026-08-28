from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureSnapshot:
    symbol: str
    event_time_ms: int
    receive_time_ns: int
    book_update_id: int
    mid_price: float
    spread: float
    spread_bps: float
    microprice: float
    imbalance_1: float
    imbalance_n: float
    bid_depth_n: float
    ask_depth_n: float
    order_flow_1s: float
    volatility_1s: float
    book_pressure: float
    compute_time_ns: int

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "symbol": self.symbol,
            "event_time_ms": self.event_time_ms,
            "receive_time_ns": self.receive_time_ns,
            "book_update_id": self.book_update_id,
            "mid_price": self.mid_price,
            "spread": self.spread,
            "spread_bps": self.spread_bps,
            "microprice": self.microprice,
            "imbalance_1": self.imbalance_1,
            "imbalance_n": self.imbalance_n,
            "bid_depth_n": self.bid_depth_n,
            "ask_depth_n": self.ask_depth_n,
            "order_flow_1s": self.order_flow_1s,
            "volatility_1s": self.volatility_1s,
            "book_pressure": self.book_pressure,
            "compute_time_ns": self.compute_time_ns,
        }
