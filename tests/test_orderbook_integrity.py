from decimal import Decimal

import pytest

from btc_research.integrity import IntegrityStatus, SequenceValidator
from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.orderbook import OrderBook


def update(
    first: int,
    final: int,
    bid_qty: str = "1",
    previous: int | None = None,
) -> DepthUpdate:
    return DepthUpdate(
        symbol="BTCUSDT",
        event_time_ms=1,
        receive_time_ns=2,
        first_update_id=first,
        final_update_id=final,
        previous_update_id=previous,
        bids=[PriceLevel("100", bid_qty)],
        asks=[PriceLevel("101", "2")],
        raw_event=b"{}",
    )


def test_validator_requires_snapshot_initialization():
    result = SequenceValidator().validate(update(101, 102, previous=100))
    assert result.status is IntegrityStatus.UNINITIALIZED


def test_validator_accepts_first_event_overlapping_snapshot():
    validator = SequenceValidator(100)
    result = validator.accept(update(99, 101, previous=98))
    assert result.status is IntegrityStatus.VALID
    assert validator.last_update_id == 101


def test_validator_requires_pu_to_match_previous_event():
    validator = SequenceValidator(100)
    assert validator.accept(update(101, 102, previous=999)).status is IntegrityStatus.VALID

    result = validator.validate(update(103, 104, previous=100))
    assert result.status is IntegrityStatus.PREVIOUS_ID_MISMATCH
    assert validator.last_update_id == 102


def test_validator_detects_gap_after_first_event():
    validator = SequenceValidator(100)
    validator.accept(update(101, 102, previous=100))

    result = validator.validate(update(104, 105, previous=102))
    assert result.status is IntegrityStatus.GAP
    assert result.expected_next_id == 103


def test_validator_detects_duplicate():
    validator = SequenceValidator(100)
    result = validator.validate(update(99, 100, previous=98))
    assert result.status is IntegrityStatus.DUPLICATE


def test_orderbook_applies_update_and_removes_zero_quantity():
    book = OrderBook.from_snapshot(
        100,
        [PriceLevel("100", "1")],
        [PriceLevel("101", "2")],
    )
    book.apply(update(101, 101, "0", previous=100))
    assert Decimal("100") not in book.bids
    assert book.best_ask() == (Decimal("101"), Decimal("2"))


def test_orderbook_rejects_sequence_gap():
    book = OrderBook.from_snapshot(
        100, [PriceLevel("100", "1")], [PriceLevel("101", "2")]
    )
    with pytest.raises(ValueError, match="sequence gap"):
        book.apply(update(102, 102, previous=101))
