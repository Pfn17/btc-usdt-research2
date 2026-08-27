from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class PriceLevel:
    price: str
    quantity: str


@dataclass(frozen=True, slots=True)
class DepthUpdate:
    symbol: str
    event_time_ms: int
    receive_time_ns: int
    first_update_id: int
    final_update_id: int
    bids: Sequence[PriceLevel]
    asks: Sequence[PriceLevel]
    raw_event: bytes


@dataclass(frozen=True, slots=True)
class ContaminatedInterval:
    start_ms: int
    end_ms: int | None
    reason: str

    def contains(self, timestamp_ms: int) -> bool:
        return timestamp_ms >= self.start_ms and (self.end_ms is None or timestamp_ms < self.end_ms)
