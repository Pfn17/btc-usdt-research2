from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Iterator


class RawEventArchive:
    """Append-only JSONL archive preserving the exact WebSocket payload bytes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, raw: bytes, receive_time_ns: int) -> None:
        record = {
            "receive_time_ns": receive_time_ns,
            "raw_b64": base64.b64encode(raw).decode("ascii"),
        }
        line = json.dumps(record, separators=(",", ":")).encode("utf-8")
        with self.path.open("ab") as handle:
            handle.write(line)
            handle.write(b"\n")

    def replay(self) -> Iterator[tuple[int, bytes]]:
        with self.path.open("rb") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                yield int(record["receive_time_ns"]), base64.b64decode(record["raw_b64"])
