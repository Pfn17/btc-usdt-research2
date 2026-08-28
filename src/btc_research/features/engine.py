from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass
from decimal import Decimal

from btc_research.marketdata.types import DepthUpdate
from btc_research.orderbook.book import OrderBook

from .metrics import FeaturePerformance
from .store import InMemoryFeatureStore
from .types import FeatureSnapshot
from .validation import validate_features


@dataclass(frozen=True, slots=True)
class _TimedPoint:
    timestamp_ms: int
    value: float


class FeatureEngine:
    """Low-allocation real-time microstructure feature calculator.

    Features are computed only from a validated local order book and depth updates.
    No network, model, or LLM work is performed in this hot path.
    """

    def __init__(self, depth_levels: int = 10, window_ms: int = 1_000, store: InMemoryFeatureStore | None = None) -> None:
        if depth_levels < 1 or window_ms < 1:
            raise ValueError("depth_levels and window_ms must be positive")
        self.depth_levels = depth_levels
        self.window_ms = window_ms
        self.store = store or InMemoryFeatureStore()
        self.metrics = FeaturePerformance()
        self._mid_history: deque[_TimedPoint] = deque()
        self._flow_history: deque[_TimedPoint] = deque()
        self._previous_qty: dict[tuple[str, str], Decimal] = {}

    def _trim(self, now_ms: int) -> None:
        cutoff = now_ms - self.window_ms
        while self._mid_history and self._mid_history[0].timestamp_ms < cutoff:
            self._mid_history.popleft()
        while self._flow_history and self._flow_history[0].timestamp_ms < cutoff:
            self._flow_history.popleft()

    @staticmethod
    def _levels(book: OrderBook, side: str, n: int) -> list[tuple[Decimal, Decimal]]:
        values = book.bids.items() if side == "bid" else book.asks.items()
        return sorted(values, reverse=(side == "bid"))[:n]

    def _order_flow(self, update: DepthUpdate) -> float:
        flow = Decimal("0")
        for side_name, levels in (("bid", update.bids), ("ask", update.asks)):
            sign = Decimal("1") if side_name == "bid" else Decimal("-1")
            for level in levels:
                key = (side_name, level.price)
                qty = Decimal(level.quantity)
                previous = self._previous_qty.get(key, Decimal("0"))
                flow += sign * (qty - previous)
                if qty == 0:
                    self._previous_qty.pop(key, None)
                else:
                    self._previous_qty[key] = qty
        return float(flow)

    def compute(self, book: OrderBook, update: DepthUpdate) -> FeatureSnapshot:
        started = time.perf_counter_ns()
        try:
            if book.last_update_id is None or update.final_update_id > book.last_update_id:
                raise ValueError("feature input book is not synchronized to update")
            bid = book.best_bid()
            ask = book.best_ask()
            if bid is None or ask is None or bid[0] >= ask[0]:
                raise ValueError("feature input book has invalid top of book")

            best_bid, bid_qty = bid
            best_ask, ask_qty = ask
            mid = (best_bid + best_ask) / Decimal("2")
            spread = best_ask - best_bid
            denom = bid_qty + ask_qty
            imbalance_1 = (bid_qty - ask_qty) / denom if denom else Decimal("0")
            micro = (best_ask * bid_qty + best_bid * ask_qty) / denom if denom else mid

            bids = self._levels(book, "bid", self.depth_levels)
            asks = self._levels(book, "ask", self.depth_levels)
            bid_depth = sum((q for _, q in bids), Decimal("0"))
            ask_depth = sum((q for _, q in asks), Decimal("0"))
            depth_denom = bid_depth + ask_depth
            imbalance_n = (bid_depth - ask_depth) / depth_denom if depth_denom else Decimal("0")

            now_ms = update.event_time_ms
            self._trim(now_ms)
            self._mid_history.append(_TimedPoint(now_ms, float(mid)))
            flow = self._order_flow(update)
            self._flow_history.append(_TimedPoint(now_ms, flow))
            flow_1s = sum(x.value for x in self._flow_history)

            returns: list[float] = []
            previous = None
            for point in self._mid_history:
                if previous is not None and point.value > 0 and previous > 0:
                    returns.append(math.log(point.value / previous))
                previous = point.value
            volatility = math.sqrt(sum(r * r for r in returns)) if returns else 0.0
            pressure = float(imbalance_n)

            elapsed = time.perf_counter_ns() - started
            snapshot = FeatureSnapshot(
                symbol=update.symbol.upper(),
                event_time_ms=update.event_time_ms,
                receive_time_ns=update.receive_time_ns,
                book_update_id=book.last_update_id,
                mid_price=float(mid),
                spread=float(spread),
                spread_bps=float(spread / mid * Decimal("10000")),
                microprice=float(micro),
                imbalance_1=float(imbalance_1),
                imbalance_n=float(imbalance_n),
                bid_depth_n=float(bid_depth),
                ask_depth_n=float(ask_depth),
                order_flow_1s=flow_1s,
                volatility_1s=volatility,
                book_pressure=pressure,
                compute_time_ns=elapsed,
            )
            validate_features(snapshot)
            self.store.put(snapshot)
            self.metrics.record(elapsed, True)
            return snapshot
        except Exception:
            self.metrics.record(time.perf_counter_ns() - started, False)
            raise
