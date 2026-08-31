from datetime import datetime, timezone

from btc_research.api import freshness


def test_freshness_from_receive_time_ns():
    now_ns = datetime.now(timezone.utc).timestamp() * 1_000_000_000
    row = {"receive_time_ns": int(now_ns) - 100_000_000}
    result = freshness(row)
    assert result["available"] is True
    assert result["stale"] is False
    assert 0 <= result["age_ms"] < 1000


def test_freshness_marks_old_data_stale():
    old_ns = int(datetime.now(timezone.utc).timestamp() * 1_000_000_000) - 10_000_000_000
    result = freshness({"receive_time_ns": old_ns})
    assert result["available"] is True
    assert result["stale"] is True
    assert result["age_ms"] >= 10_000


def test_missing_data_is_not_fabricated():
    result = freshness(None)
    assert result == {"available": False, "stale": True, "age_ms": None}
