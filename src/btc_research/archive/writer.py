from __future__ import annotations

import hashlib
import json
import os
import shutil
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
    """Bounded raw-event archive with size rotation and oldest-first retention.

    The bounded mode is intentional for small ephemeral volumes such as Railway
    Free. Long-term immutable storage should be moved to durable object storage
    before relying on replay beyond the local retention window.
    """

    def __init__(self, root: str | Path = "./data/raw", min_free_mb: int | None = None, max_archive_mb: int | None = None, rotate_mb: int | None = None) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        configured_min = os.environ.get("BTC_ARCHIVE_MIN_FREE_MB", "64")
        configured_max = os.environ.get("BTC_ARCHIVE_MAX_MB", "300")
        configured_rotate = os.environ.get("BTC_ARCHIVE_ROTATE_MB", "32")
        self.min_free_bytes = (min_free_mb if min_free_mb is not None else int(configured_min)) * 1024 * 1024
        self.max_archive_bytes = (max_archive_mb if max_archive_mb is not None else int(configured_max)) * 1024 * 1024
        self.rotate_bytes = (rotate_mb if rotate_mb is not None else int(configured_rotate)) * 1024 * 1024
        if self.max_archive_bytes <= 0 or self.rotate_bytes <= 0:
            raise ValueError("archive size limits must be positive")
        if self.rotate_bytes > self.max_archive_bytes:
            raise ValueError("rotate size cannot exceed archive retention size")

    def _files(self) -> list[Path]:
        return sorted((p for p in self.root.glob("**/depth*.jsonl") if p.is_file()), key=lambda p: (p.stat().st_mtime_ns, str(p)))

    def _total_bytes(self) -> int:
        return sum(p.stat().st_size for p in self._files())

    def _prune_oldest(self, protected: Path | None = None) -> None:
        files = self._files()
        total = sum(p.stat().st_size for p in files)
        target = self.max_archive_bytes
        for path in files:
            if total <= target:
                break
            if protected is not None and path == protected:
                continue
            size = path.stat().st_size
            path.unlink(missing_ok=True)
            total -= size

    def path_for(self, symbol: str, event_time_ms: int) -> Path:
        dt = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc)
        directory = self.root / symbol.upper() / dt.strftime("%Y-%m-%d")
        directory.mkdir(parents=True, exist_ok=True)
        base = directory / "depth.jsonl"
        if not base.exists() or base.stat().st_size < self.rotate_bytes:
            return base
        index = 1
        while True:
            candidate = directory / f"depth-{index:04d}.jsonl"
            if not candidate.exists() or candidate.stat().st_size < self.rotate_bytes:
                return candidate
            index += 1

    def append(self, update: DepthUpdate) -> Path:
        record = ArchiveRecord.from_update(update).to_jsonl()
        usage = shutil.disk_usage(self.root)
        if usage.free < self.min_free_bytes:
            self._prune_oldest()
            usage = shutil.disk_usage(self.root)
        if usage.free < self.min_free_bytes:
            raise OSError(
                f"raw archive storage below safety margin after retention: free={usage.free} bytes, "
                f"required={self.min_free_bytes} bytes"
            )

        path = self.path_for(update.symbol, update.event_time_ms)
        with path.open("ab") as fh:
            fh.write(record)
            fh.flush()
        self._prune_oldest(protected=path)
        return path
