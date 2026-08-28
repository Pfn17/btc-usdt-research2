from decimal import Decimal

import pytest

from btc_research.features import FeatureEngine, FeatureValidationError, InMemoryFeatureStore, validate_features
from btc_research.features.types import FeatureSnapshot
from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.orderbook.book import OrderBook


def make_book() -> OrderBook:
    return OrderBook.from_snapshot(
        100,
        [PriceLevel("100", "2"), PriceLevel("99", "3"), PriceLevel("98", "4")],
        [PriceLevel("101", "1"), PriceLevel("102", "2"), PriceLevel("103", "3")],
    )


def make_update(u: int, bids=None, asks=None, t: int = 1_000) -> DepthUpdate:
    return DepthUpdate(
        "BTCUSDT", t, 123_000, u, u,
        bids or [PriceLevel("100", "2")],
        asks or [PriceLevel("101", "1")],
        b"{}",
    )


def test_feature_engine_core_features() -> None:
    book = make_book()
    engine = FeatureEngine(depth_levels=2)
    update = make_update(101)
    book.apply(update)
    snap = engine.compute(book, update)
    assert snap.mid_price == 100.5
    assert snap.spread == 1.0
    assert snap.spread_bps == pytest.approx(99.5024876)
    assert snap.microprice == pytest.approx(100.6666667)
    assert snap.imbalance_1 == pytest.approx(1 / 3)
    assert snap.imbalance_n == pytest.approx(2 / 7)
    assert snap.order_flow_1s == 0.0
    assert snap.volatility_1s == 0.0


def test_order_flow_uses_book_as_initial_baseline() -> None:
    book = make_book()
    engine = FeatureEngine()
    first = make_update(101)
    book.apply(first)
    engine.compute(book, first)
    update = make_update(102, bids=[PriceLevel("100", "3")], asks=[], t=1_001)
    book.apply(update)
    snap = engine.compute(book, update)
    assert snap.order_flow_1s == pytest.approx(1.0)


def test_store_keeps_latest_and_bounded_history() -> None:
    store = InMemoryFeatureStore(max_history=2)
    engine = FeatureEngine(store=store)
    book = make_book()
    for u in (101, 102, 103):
        update = make_update(u, t=u * 10)
        book.apply(update)
        engine.compute(book, update)
    assert len(store) == 2
    assert store.latest("btcusdt").book_update_id == 103


def test_validation_rejects_nonfinite() -> None:
    snapshot = FeatureSnapshot("BTCUSDT", 1, 1, 1, float("nan"), 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1)
    with pytest.raises(FeatureValidationError):
        validate_features(snapshot)


def test_engine_rejects_unsynchronized_update() -> None:
    engine = FeatureEngine()
    book = make_book()
    with pytest.raises(ValueError, match="not synchronized"):
        engine.compute(book, make_update(1010))
