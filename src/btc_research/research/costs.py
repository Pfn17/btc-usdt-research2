from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostModel:
    fee_bps: float
    half_spread_bps: float
    slippage_bps: float
    latency_bps: float = 0.0

    def __post_init__(self) -> None:
        if min(self.fee_bps, self.half_spread_bps, self.slippage_bps, self.latency_bps) < 0:
            raise ValueError("cost components cannot be negative")

    @property
    def round_trip_bps(self) -> float:
        return 2.0 * (self.fee_bps + self.half_spread_bps + self.slippage_bps + self.latency_bps)


@dataclass(frozen=True, slots=True)
class CostResult:
    gross_return_pct: float
    cost_pct: float
    net_return_pct: float


def apply_cost(gross_return_pct: float, model: CostModel) -> CostResult:
    cost_pct = model.round_trip_bps / 100.0
    return CostResult(gross_return_pct, cost_pct, gross_return_pct - cost_pct)
