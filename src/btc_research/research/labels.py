from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class TripleBarrierLabel:
    label: int
    exit_time_ms: int
    exit_price: float
    reason: str
    return_pct: float


def triple_barrier_label(
    entry_time_ms: int,
    entry_price: float,
    future_times_ms: Sequence[int],
    future_prices: Sequence[float],
    take_profit_pct: float,
    stop_loss_pct: float,
    horizon_ms: int,
) -> TripleBarrierLabel:
    if entry_price <= 0 or take_profit_pct <= 0 or stop_loss_pct <= 0 or horizon_ms <= 0:
        raise ValueError("entry price, barriers and horizon must be positive")
    if len(future_times_ms) != len(future_prices):
        raise ValueError("future_times_ms and future_prices must have equal length")
    upper = entry_price * (1.0 + take_profit_pct)
    lower = entry_price * (1.0 - stop_loss_pct)
    deadline = entry_time_ms + horizon_ms
    last_time, last_price = entry_time_ms, entry_price
    for timestamp, price in zip(future_times_ms, future_prices):
        if timestamp < entry_time_ms:
            raise ValueError("future observations must not precede entry")
        if timestamp > deadline:
            break
        if price <= 0:
            raise ValueError("future prices must be positive")
        last_time, last_price = timestamp, price
        # With close-only data, same-bar TP/SL ordering is unknowable; reject ambiguity.
        hit_tp = price >= upper
        hit_sl = price <= lower
        if hit_tp and hit_sl:
            return TripleBarrierLabel(0, timestamp, price, "ambiguous_barrier", price / entry_price - 1.0)
        if hit_tp:
            return TripleBarrierLabel(1, timestamp, price, "take_profit", price / entry_price - 1.0)
        if hit_sl:
            return TripleBarrierLabel(-1, timestamp, price, "stop_loss", price / entry_price - 1.0)
    return TripleBarrierLabel(0, last_time, last_price, "time_barrier", last_price / entry_price - 1.0)
