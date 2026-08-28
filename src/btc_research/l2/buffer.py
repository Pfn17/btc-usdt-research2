from __future__ import annotations

from collections import deque
from typing import Deque

from btc_research.marketdata.types import DepthUpdate


class EventBuffer:
    """Bounded FIFO buffer used while a REST snapshot is being acquired.

    ``swap`` is intentionally synchronous: in the asyncio event loop it gives
    the collector an atomic hand-off point between the pre-snapshot buffer and
    events arriving after the snapshot boundary.
    """

    def __init__(self, maxlen: int = 10_000) -> None:
        if maxlen < 1:
            raise ValueError("maxlen must be positive")
        self._events: Deque[DepthUpdate] = deque(maxlen=maxlen)
        self.dropped = 0

    def append(self, event: DepthUpdate) -> None:
        if len(self._events) == self._events.maxlen:
            self.dropped += 1
        self._events.append(event)

    def clear(self) -> None:
        self._events.clear()

    def snapshot(self) -> list[DepthUpdate]:
        return list(self._events)

    def swap(self) -> list[DepthUpdate]:
        """Atomically detach all currently buffered events and reset the queue."""
        events = list(self._events)
        self._events.clear()
        return events

    def __len__(self) -> int:
        return len(self._events)
