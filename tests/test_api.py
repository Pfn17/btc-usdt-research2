from datetime import datetime, timezone

from btc_research.api import freshness, public_aggregate_metrics


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


def test_public_aggregate_excludes_edge_identity_and_parameters():
    result = public_aggregate_metrics({
        "net_profit": 12.5,
        "gross_profit": 20.0,
        "gross_loss": -7.5,
        "closed_observations": 40,
        "wins": 23,
        "losses": 17,
        "win_rate": 0.575,
        "average_outcome": 0.3125,
        "profit_factor": 2.66,
        "maximum_drawdown": -4.0,
        "status": "VALIDATED_AGGREGATE",
        "trading_enabled": False,
        "hypothesis_key": "SECRET_EDGE",
        "feature_set": {"private": True},
        "entry_rule": "private",
        "direction": "LONG",
        "parameters": {"threshold": 99},
    })
    assert result["net_profit"] == 12.5
    assert result["win_rate"] == 0.575
    assert "hypothesis_key" not in result
    assert "feature_set" not in result
    assert "entry_rule" not in result
    assert "direction" not in result
    assert "parameters" not in result


def test_public_aggregate_missing_row_is_unavailable():
    assert public_aggregate_metrics(None) == {"status": "UNAVAILABLE", "trading_enabled": False}
