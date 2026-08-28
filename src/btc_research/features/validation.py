from __future__ import annotations

import math

from .types import FeatureSnapshot


class FeatureValidationError(ValueError):
    pass


def validate_features(features: FeatureSnapshot) -> None:
    """Reject malformed, non-finite, or structurally impossible features."""
    if not features.symbol:
        raise FeatureValidationError("symbol is empty")
    if features.book_update_id < 0 or features.event_time_ms < 0 or features.receive_time_ns < 0:
        raise FeatureValidationError("invalid timestamp or update id")

    numeric = (
        features.mid_price,
        features.spread,
        features.spread_bps,
        features.microprice,
        features.imbalance_1,
        features.imbalance_n,
        features.bid_depth_n,
        features.ask_depth_n,
        features.order_flow_1s,
        features.volatility_1s,
        features.book_pressure,
    )
    if not all(math.isfinite(x) for x in numeric):
        raise FeatureValidationError("non-finite feature value")
    if features.mid_price <= 0 or features.microprice <= 0:
        raise FeatureValidationError("price features must be positive")
    if features.spread < 0 or features.spread_bps < 0:
        raise FeatureValidationError("spread cannot be negative")
    if features.bid_depth_n < 0 or features.ask_depth_n < 0:
        raise FeatureValidationError("depth cannot be negative")
    if not -1.000001 <= features.imbalance_1 <= 1.000001:
        raise FeatureValidationError("imbalance_1 outside [-1, 1]")
    if not -1.000001 <= features.imbalance_n <= 1.000001:
        raise FeatureValidationError("imbalance_n outside [-1, 1]")
    if features.volatility_1s < 0:
        raise FeatureValidationError("volatility cannot be negative")
