from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class WalkForwardSplit:
    fold: int
    train_start_ms: int
    train_end_ms: int
    test_start_ms: int
    test_end_ms: int
    purge_ms: int
    embargo_ms: int


def generate_walk_forward_splits(
    timestamps_ms: Sequence[int],
    train_ms: int,
    test_ms: int,
    purge_ms: int,
    embargo_ms: int,
    step_ms: int | None = None,
) -> list[WalkForwardSplit]:
    if not timestamps_ms or min(train_ms, test_ms) <= 0 or min(purge_ms, embargo_ms) < 0:
        raise ValueError("timestamps, train_ms and test_ms must be valid")
    ordered = list(timestamps_ms)
    if ordered != sorted(ordered):
        raise ValueError("timestamps must be monotonically ordered")
    if len(set(ordered)) != len(ordered):
        raise ValueError("timestamps must be unique")
    step = step_ms or test_ms
    if step <= 0:
        raise ValueError("step_ms must be positive")
    start = ordered[0]
    end = ordered[-1]
    splits: list[WalkForwardSplit] = []
    fold = 0
    while True:
        train_start = start
        train_end = train_start + train_ms
        test_start = train_end + purge_ms
        test_end = test_start + test_ms
        if test_end > end:
            break
        # Embargo is represented as a forbidden interval after the test set.
        splits.append(WalkForwardSplit(fold, train_start, train_end, test_start, test_end, purge_ms, embargo_ms))
        fold += 1
        start += step
    return splits


def purge_and_embargo_indices(
    timestamps_ms: Sequence[int],
    split: WalkForwardSplit,
) -> tuple[list[int], list[int]]:
    train: list[int] = []
    test: list[int] = []
    embargo_end = split.test_end + split.embargo_ms
    for i, ts in enumerate(timestamps_ms):
        if split.train_start_ms <= ts < split.train_end_ms:
            train.append(i)
        if split.test_start_ms <= ts < split.test_end_ms:
            test.append(i)
        if split.test_end_ms <= ts < embargo_end:
            continue
    return train, test
