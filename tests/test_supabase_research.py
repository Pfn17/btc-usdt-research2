import os

import pytest

from btc_research.features.types import FeatureSnapshot
from btc_research.research import ExperimentFamily, Hypothesis
from btc_research.research.supabase import SupabaseResearchClient


def test_feature_snapshot_payload_matches_production_contract() -> None:
    snapshot = FeatureSnapshot(
        symbol="BTCUSDT",
        event_time_ms=1,
        receive_time_ns=2,
        book_update_id=3,
        mid_price=100.0,
        spread=0.1,
        spread_bps=10.0,
        microprice=100.01,
        imbalance_1=0.1,
        imbalance_n=0.2,
        bid_depth_n=10.0,
        ask_depth_n=8.0,
        order_flow_1s=1.0,
        volatility_1s=0.01,
        book_pressure=0.1,
        compute_time_ns=400_000,
    )
    payload = {"session_id": "session", **snapshot.as_dict()}
    SupabaseResearchClient._validate_payload("feature_snapshots", payload)


def test_feature_snapshot_contract_rejects_unknown_column() -> None:
    payload = {
        "session_id": "session",
        "symbol": "BTCUSDT",
        "event_time_ms": 1,
        "receive_time_ns": 2,
        "book_update_id": 3,
        "mid_price": 100.0,
        "spread": 0.1,
        "spread_bps": 10.0,
        "microprice": 100.01,
        "imbalance_1": 0.1,
        "imbalance_n": 0.2,
        "bid_depth_n": 10.0,
        "ask_depth_n": 8.0,
        "order_flow_1s": 1.0,
        "volatility_1s": 0.01,
        "book_pressure": 0.1,
        "compute_time_ns": 400_000,
        "not_a_real_column": 123,
    }
    with pytest.raises(ValueError, match="unknown columns"):
        SupabaseResearchClient._validate_payload("feature_snapshots", payload)


def test_paper_signal_contract_rejects_unknown_column() -> None:
    payload = {
        "session_id": "session",
        "event_time_ms": 1,
        "direction": "LONG",
        "data_quality": "valid",
        "risk_status": "paper",
        "unexpected": 123,
    }
    with pytest.raises(ValueError, match="unknown columns"):
        SupabaseResearchClient._validate_payload("paper_signals", payload)


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"), reason="Supabase integration credentials not configured")
def test_supabase_can_insert_and_read_family() -> None:
    family = ExperimentFamily("test-family", "integration-test")
    with SupabaseResearchClient() as db:
        rows = db.insert_family(family)
        assert rows
        fetched = db.select("experiment_families", "select=family_key&family_key=eq.test-family")
        assert fetched and fetched[0]["family_key"] == "test-family"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"), reason="Supabase integration credentials not configured")
def test_supabase_can_insert_hypothesis() -> None:
    family = ExperimentFamily("test-family-h", "integration-test")
    hypothesis = Hypothesis.create("test-hypothesis", family.family_id, "test", 60, "two_sided")
    with SupabaseResearchClient() as db:
        db.insert_family(family)
        rows = db.insert_hypothesis(hypothesis)
        assert rows and rows[0]["hypothesis_key"] == hypothesis.hypothesis_id
