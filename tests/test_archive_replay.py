from pathlib import Path

from btc_research.archive.reader import ArchiveReader
from btc_research.archive.writer import ArchiveWriter
from btc_research.marketdata.types import DepthUpdate, PriceLevel
from btc_research.replay.engine import ReplayEngine, depth_update_from_archive_record


def make_event(uid: int, raw: bytes = b'{"e":"depthUpdate"}') -> DepthUpdate:
    return DepthUpdate("BTCUSDT", 1_700_000_000_000 + uid, 1_000_000 + uid, uid, uid, [PriceLevel("100", "1")], [PriceLevel("101", "2")], raw)


def test_archive_roundtrip_preserves_raw_and_receive_time(tmp_path: Path) -> None:
    writer = ArchiveWriter(tmp_path)
    writer.append(make_event(11))
    record = next(ArchiveReader(tmp_path).records("BTCUSDT"))
    assert record.raw_event == b'{"e":"depthUpdate"}'
    assert record.receive_time_ns == 1_000_011


def test_bounded_archive_rotates_and_retains_recent_data(tmp_path: Path) -> None:
    writer = ArchiveWriter(tmp_path, min_free_mb=1, max_archive_mb=1, rotate_mb=1)
    for uid in range(1, 5000):
        writer.append(make_event(uid, b"x" * 400))

    files = ArchiveReader(tmp_path).files("BTCUSDT")
    total = sum(path.stat().st_size for path in files)
    assert files
    assert total <= 1 * 1024 * 1024
    assert any(path.name.startswith("depth-") for path in files)
    records = list(ArchiveReader(tmp_path).records("BTCUSDT"))
    assert records
    assert records[-1].final_update_id == 4999


def test_replay_is_deterministic() -> None:
    from btc_research.marketdata.types import PriceLevel
    events = [make_event(11), make_event(12)]
    a = ReplayEngine(10, [PriceLevel("99", "1")], [PriceLevel("101", "2")]).replay(events)
    b = ReplayEngine(10, [PriceLevel("99", "1")], [PriceLevel("101", "2")]).replay(events)
    assert a == b
    assert a.final_update_id == 12


def test_archive_raw_event_decodes_to_depth_update() -> None:
    raw = b'{"e":"depthUpdate","E":1700000000000,"s":"BTCUSDT","U":11,"u":11,"b":[["100","1"]],"a":[["101","2"]]}'
    record = make_event(11, raw)
    decoded = depth_update_from_archive_record(record)
    assert decoded.receive_time_ns == record.receive_time_ns
    assert decoded.final_update_id == 11
