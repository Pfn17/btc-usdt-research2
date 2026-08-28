from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from btc_research.marketdata.types import DepthUpdate


class IntegrityStatus(str, Enum):
    VALID = "VALID"
    DUPLICATE = "DUPLICATE"
    GAP = "GAP"


@dataclass(frozen=True)
class IntegrityResult:
    status: IntegrityStatus
    expected_next_id: int
    first_update_id: int
    final_update_id: int


class SequenceValidator:
    """Validate contiguous Binance depth update IDs before applying them."""

    def __init__(self, last_update_id: int | None = None) -> None:
        self.last_update_id = last_update_id

    def validate(self, update: DepthUpdate) -> IntegrityResult:
        if self.last_update_id is None:
            return IntegrityResult(
                IntegrityStatus.VALID,
                update.first_update_id,
                update.first_update_id,
                update.final_update_id,
            )

        expected = self.last_update_id + 1
        if update.final_update_id <= self.last_update_id:
            return IntegrityResult(
                IntegrityStatus.DUPLICATE,
                expected,
                update.first_update_id,
                update.final_update_id,
            )
        if update.first_update_id > expected:
            return IntegrityResult(
                IntegrityStatus.GAP,
                expected,
                update.first_update_id,
                update.final_update_id,
            )
        return IntegrityResult(
            IntegrityStatus.VALID,
            expected,
            update.first_update_id,
            update.final_update_id,
        )

    def accept(self, update: DepthUpdate) -> IntegrityResult:
        result = self.validate(update)
        if result.status is IntegrityStatus.VALID:
            self.last_update_id = update.final_update_id
        return result
