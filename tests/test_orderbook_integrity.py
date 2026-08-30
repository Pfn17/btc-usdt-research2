from btc_research.integrity.validator import IntegrityStatus, SequenceValidator
from btc_research.marketdata.types import DepthUpdate, PriceLevel


def update(first: int, final: int) -> DepthUpdate:
    return DepthUpdate("BTCUSDT", 1_000, 2_000, first, final, [PriceLevel("100", "1")], [PriceLevel("101", "1")], b"{}", first - 1)


def test_validator_accepts_contiguous_updates():
    validator = SequenceValidator(100)
    assert validator.accept(update(101, 102)).status is IntegrityStatus.VALID
    assert validator.last_update_id == 102


def test_validator_rejects_gap():
    validator = SequenceValidator(100)
    assert validator.validate(update(102, 103)).status is IntegrityStatus.GAP
    assert validator.last_update_id == 100


def test_validator_marks_duplicate():
    validator = SequenceValidator(100)
    assert validator.validate(update(99, 100)).status is IntegrityStatus.DUPLICATE
    assert validator.last_update_id == 100
