from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from btc_research.marketdata.types import DepthUpdate


class IntegrityStatus(str, Enum):
    VALID = "VALID"
    DUPLICATE = "DUPLICATE"
    GAP = "GAP"
    PREVIOUS_ID_MISMATCH = "PREVIOUS_ID_MISMATCH"


@dataclass(frozen=True)
class IntegrityResult:
    status: IntegrityStatus
    expected_next_id: int
    first_update_id: int
    final_update_id: int


class SequenceValidator:
    """Validate USDⓈ-M Futures diff-depth continuity.

    The first stream event after a REST snapshot must satisfy:
        U <= snapshot_last_update_id + 1 <= u

    Every later event must satisfy:
        pu == previous accepted event's u

    Duplicate/old events are ignored. Any sequence break invalidates the
    stream and requires snapshot resynchronization by the caller.
    """

    def __init__(self, last_update_id: int | None = None) -> None:
        self.last_update_id = last_update_id
        self._seen_stream_event = False

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

        if self._seen_stream_event:
            if update.previous_update_id != self.last_update_id:
                return IntegrityResult(
                    IntegrityStatus.PREVIOUS_ID_MISMATCH,
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
        elif not (update.first_update_id <= expected <= update.final_update_id):
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
            self._seen_stream_event = True
        return result
