"""H-C2 conditional microstructure state construction.

Pure feature/state helpers. No trading or order execution is performed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Optional


@dataclass(frozen=True)
class HC2State:
    """Frozen state used by the H-C2 research experiment."""

    return_5s: float
    return_15s: float
    return_30s: float
    rv_30s: float
    volume_z: float
    volume_accel: float
    book_imbalance: float
    microprice_dev_bps: float
    spread_bps: float
    depth_imbalance: float
    order_flow_imbalance: float
    flow_agreement: float


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def safe_ratio(num: float, den: float) -> Optional[float]:
    if not isfinite(num) or not isfinite(den) or den == 0:
        return None
    return num / den


def microprice(mid: float, bid: float, ask: float, bid_size: float, ask_size: float) -> Optional[float]:
    """Size-weighted microprice; returns None when inputs are unusable."""
    total = bid_size + ask_size
    if total <= 0 or not all(isfinite(x) for x in (mid, bid, ask, bid_size, ask_size)):
        return None
    return (ask * bid_size + bid * ask_size) / total


def imbalance(bid_size: float, ask_size: float) -> Optional[float]:
    """Normalized depth/order-flow imbalance in [-1, 1]."""
    value = safe_ratio(bid_size - ask_size, bid_size + ask_size)
    return None if value is None else _clip(value)


def build_hc2_state(
    *,
    return_5s: float,
    return_15s: float,
    return_30s: float,
    rv_30s: float,
    volume_z: float,
    volume_accel: float,
    mid: float,
    bid: float,
    ask: float,
    bid_depth: float,
    ask_depth: float,
    signed_flow: float,
    total_flow: float,
) -> Optional[HC2State]:
    """Build a deterministic, timestamp-local H-C2 state.

    The caller must supply values computed only from observations at or before
    the signal timestamp. Future labels are intentionally absent from this
    function.
    """
    mp = microprice(mid, bid, ask, bid_depth, ask_depth)
    bi = imbalance(bid_depth, ask_depth)
    foi = safe_ratio(signed_flow, total_flow)
    if mp is None or bi is None or foi is None or mid <= 0 or ask < bid:
        return None
    spread_bps = (ask - bid) / mid * 10_000
    micro_dev = (mp - mid) / mid * 10_000
    flow = _clip(foi)
    agreement = (1.0 if bi * flow > 0 else 0.0) if bi != 0 and flow != 0 else 0.0
    return HC2State(
        return_5s=return_5s,
        return_15s=return_15s,
        return_30s=return_30s,
        rv_30s=rv_30s,
        volume_z=volume_z,
        volume_accel=volume_accel,
        book_imbalance=bi,
        microprice_dev_bps=micro_dev,
        spread_bps=spread_bps,
        depth_imbalance=bi,
        order_flow_imbalance=flow,
        flow_agreement=agreement,
    )
