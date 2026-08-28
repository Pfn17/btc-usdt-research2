from decimal import Decimal

import pytest

from btc_research.integrity import IntegrityStatus, SequenceValidator
from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.orderbook import OrderBook


def update(first: int, final: int, bid_qty: str = "1") -> DepthUpdate:
    return DepthUpdate(
        symbol="BTCUSDT",
        exchange_timestamp_ms=1,
        local_receive_timestamp_ms=2,
        first_update_id=first,
        final_update_id=final,
        previous_update_id=None,
        bids=[PriceLevel("100", bid_qty)],
        asks=[PriceLevel("101", "2")],
    )


def test_validator_accepts_contiguous_updates():
    validator = SequenceValidator(100)
    assert validator.accept(update(101, 102)).status is IntegrityStatus.VALID
    assert validator.last_update_id == 102


def test_validator_detects_gap():
    validator = SequenceValidator(100)
    result = validator.validate(update(103, 104))
    assert result.status is IntegrityStatus.GAP
    assert result.expected_next_id == 101


def test_validator_detects_duplicate():
    validator = SequenceValidator(100)
    result = validator.validate(update(99, 100))
    assert result.status is IntegrityStatus.DUPLICATE


def test_orderbook_applies_update_and_removes_zero_quantity():
    book = OrderBook.from_snapshot(
        100,
        [PriceLevel("100", "1")],
        [PriceLevel("101", "2")],
    )
    book.apply(update(101, 101, "0"))
    assert Decimal("100") not in book.bids
    assert book.best_ask() == (Decimal("101"), Decimal("2"))


def test_orderbook_rejects_sequence_gap():
    book = OrderBook.from_snapshot(100, [PriceLevel("100", "1")], [PriceLevel("101", "2")])
    with pytest.raises(ValueError, match="sequence gap"):
        book.apply(update(102, 102))
