from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from .writer import ArchiveRecord


class ArchiveReader:
    """Deterministic reader for append-only archive files."""

    def __init__(self, root: str | Path = "./data/raw") -> None:
        self.root = Path(root)

    def files(self, symbol: str, start_date: str | None = None, end_date: str | None = None) -> list[Path]:
        base = self.root / symbol.upper()
        if not base.exists():
            return []
        paths = sorted(base.glob("*/depth.jsonl"))
        if start_date:
            paths = [p for p in paths if p.parent.name >= start_date]
        if end_date:
            paths = [p for p in paths if p.parent.name <= end_date]
        return paths

    def records(self, symbol: str, start_date: str | None = None, end_date: str | None = None) -> Iterator[ArchiveRecord]:
        for path in self.files(symbol, start_date, end_date):
            with path.open("rb") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    raw = bytes.fromhex(obj["raw_event_hex"])
                    if obj["raw_sha256"] != __import__("hashlib").sha256(raw).hexdigest():
                        raise ValueError(f"archive checksum mismatch: {path}")
                    yield ArchiveRecord(
                        symbol=obj["symbol"], event_time_ms=int(obj["event_time_ms"]),
                        receive_time_ns=int(obj["receive_time_ns"]),
                        first_update_id=int(obj["first_update_id"]),
                        final_update_id=int(obj["final_update_id"]), raw_event=raw,
                    )
