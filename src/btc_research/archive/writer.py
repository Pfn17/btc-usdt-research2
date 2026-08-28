from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from btc_research.marketdata.types import DepthUpdate


@dataclass(frozen=True, slots=True)
class ArchiveRecord:
    symbol: str
    event_time_ms: int
    receive_time_ns: int
    first_update_id: int
    final_update_id: int
    raw_event: bytes

    @property
    def raw_sha256(self) -> str:
        return hashlib.sha256(self.raw_event).hexdigest()

    def to_jsonl(self) -> bytes:
        return (json.dumps({
            "symbol": self.symbol,
            "event_time_ms": self.event_time_ms,
            "receive_time_ns": self.receive_time_ns,
            "first_update_id": self.first_update_id,
            "final_update_id": self.final_update_id,
            "raw_event_hex": self.raw_event.hex(),
            "raw_sha256": self.raw_sha256,
        }, separators=(",", ":"), sort_keys=True) + "\n").encode()

    @classmethod
    def from_update(cls, update: DepthUpdate) -> "ArchiveRecord":
        return cls(update.symbol, update.event_time_ms, update.receive_time_ns, update.first_update_id, update.final_update_id, update.raw_event)


class ArchiveWriter:
    """Append-only raw event archive with deterministic metadata and daily rotation."""

    def __init__(self, root: str | Path = "./data/raw") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, symbol: str, event_time_ms: int) -> Path:
        dt = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc)
        directory = self.root / symbol.upper() / dt.strftime("%Y-%m-%d")
        directory.mkdir(parents=True, exist_ok=True)
        return directory / "depth.jsonl"

    def append(self, update: DepthUpdate) -> Path:
        path = self.path_for(update.symbol, update.event_time_ms)
        with path.open("ab") as fh:
            fh.write(ArchiveRecord.from_update(update).to_jsonl())
            fh.flush()
        return path
