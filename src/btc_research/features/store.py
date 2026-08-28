from __future__ import annotations

from collections import deque
from threading import Lock

from .types import FeatureSnapshot


class InMemoryFeatureStore:
    """Bounded latest-value cache plus optional feature history."""

    def __init__(self, max_history: int = 100_000) -> None:
        if max_history < 1:
            raise ValueError("max_history must be positive")
        self._latest: dict[str, FeatureSnapshot] = {}
        self._history: deque[FeatureSnapshot] = deque(maxlen=max_history)
        self._lock = Lock()

    def put(self, snapshot: FeatureSnapshot) -> None:
        with self._lock:
            self._latest[snapshot.symbol] = snapshot
            self._history.append(snapshot)

    def latest(self, symbol: str) -> FeatureSnapshot | None:
        with self._lock:
            return self._latest.get(symbol.upper())

    def history(self, symbol: str | None = None) -> list[FeatureSnapshot]:
        with self._lock:
            if symbol is None:
                return list(self._history)
            key = symbol.upper()
            return [x for x in self._history if x.symbol == key]

    def __len__(self) -> int:
        with self._lock:
            return len(self._history)
