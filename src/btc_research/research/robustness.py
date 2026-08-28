from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Sequence


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    mean: float
    ci_low: float
    ci_high: float
    samples: int
    block_size: int


def block_bootstrap_mean(values: Sequence[float], block_size: int = 10, samples: int = 2_000, seed: int = 0) -> BootstrapResult:
    if not values or block_size < 1 or samples < 1:
        raise ValueError("values, block_size and samples must be valid")
    if block_size > len(values):
        raise ValueError("block_size cannot exceed sample count")
    rng = random.Random(seed)
    n = len(values)
    means: list[float] = []
    blocks = math.ceil(n / block_size)
    for _ in range(samples):
        sample: list[float] = []
        for _ in range(blocks):
            start = rng.randrange(0, n - block_size + 1)
            sample.extend(values[start:start + block_size])
        means.append(sum(sample[:n]) / n)
    means.sort()
    return BootstrapResult(sum(values) / n, means[int(0.025 * samples)], means[min(samples - 1, int(0.975 * samples))], samples, block_size)


def benjamini_hochberg(p_values: Sequence[float], q: float = 0.05) -> list[bool]:
    if not 0 < q < 1 or any(p < 0 or p > 1 for p in p_values):
        raise ValueError("p-values must be in [0,1] and q must be in (0,1)")
    ordered = sorted(enumerate(p_values), key=lambda item: item[1])
    cutoff = -1
    for rank, (_, p) in enumerate(ordered, start=1):
        if p <= q * rank / len(ordered):
            cutoff = rank
    accepted = [False] * len(p_values)
    if cutoff >= 0:
        for rank, (idx, _) in enumerate(ordered, start=1):
            if rank <= cutoff:
                accepted[idx] = True
    return accepted


def uniqueness_weights(intervals: Sequence[tuple[int, int]]) -> list[float]:
    if any(end <= start for start, end in intervals):
        raise ValueError("label intervals must have end > start")
    if not intervals:
        return []
    weights: list[float] = []
    for start, end in intervals:
        active = sum(1 for other_start, other_end in intervals if other_start < end and other_end > start)
        weights.append(1.0 / active)
    return weights
