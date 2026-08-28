from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureMetrics:
    computed: int
    rejected: int
    total_compute_ns: int
    max_compute_ns: int

    @property
    def mean_compute_ns(self) -> float:
        return self.total_compute_ns / self.computed if self.computed else 0.0

    @property
    def rejection_rate(self) -> float:
        total = self.computed + self.rejected
        return self.rejected / total if total else 0.0


class FeaturePerformance:
    def __init__(self) -> None:
        self.computed = 0
        self.rejected = 0
        self.total_compute_ns = 0
        self.max_compute_ns = 0

    def record(self, compute_ns: int, accepted: bool = True) -> None:
        if accepted:
            self.computed += 1
            self.total_compute_ns += compute_ns
            self.max_compute_ns = max(self.max_compute_ns, compute_ns)
        else:
            self.rejected += 1

    def snapshot(self) -> FeatureMetrics:
        return FeatureMetrics(self.computed, self.rejected, self.total_compute_ns, self.max_compute_ns)
