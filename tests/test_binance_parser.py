import json

import pytest

from btc_research.marketdata.binance import BinanceFuturesMarketData


def sample_event() -> bytes:
    return json.dumps(
        {
            "e": "depthUpdate",
            "E": 1000,
            "T": 999,
            "s": "BTCUSDT",
            "U": 101,
            "u": 102,
            "pu": 100,
            "b": [["100.0", "1.25"]],
            "a": [["101.0", "2.50"]],
        },
        separators=(",", ":"),
    ).encode()


def test_decode_futures_depth_preserves_required_sequence_fields():
    raw = sample_event()
    update = BinanceFuturesMarketData.decode_depth_message(raw)

    assert update.symbol == "BTCUSDT"
    assert update.event_time_ms == 1000
    assert update.transaction_time_ms == 999
    assert update.first_update_id == 101
    assert update.final_update_id == 102
    assert update.previous_update_id == 100
    assert update.raw_event == raw
    assert update.bids[0].price == "100.0"
    assert update.bids[0].quantity == "1.25"


def test_decode_rejects_non_depth_events():
    payload = json.loads(sample_event())
    payload["e"] = "aggTrade"
    with pytest.raises(ValueError, match="unexpected Binance Futures event type"):
        BinanceFuturesMarketData.decode_depth_message(json.dumps(payload))


def test_decode_rejects_missing_pu():
    payload = json.loads(sample_event())
    del payload["pu"]
    with pytest.raises(ValueError, match="missing required sequence fields"):
        BinanceFuturesMarketData.decode_depth_message(json.dumps(payload))
