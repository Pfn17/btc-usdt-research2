import pytest

from btc_research.research.paper import simulate_fill


def test_long_paper_fill_applies_round_trip_cost():
    fill = simulate_fill("LONG", 100.0, 100.10, quantity=2.0, fee_bps_per_side=4.0, slippage_bps_per_side=1.0)
    assert fill.signed_return_bps == pytest.approx(10.0)
    assert fill.cost_bps == pytest.approx(10.0)
    assert fill.net_pnl == pytest.approx(0.0)
    assert fill.as_dict()["execution_mode"] == "PAPER_ONLY"


def test_short_paper_fill_has_correct_sign():
    fill = simulate_fill("SHORT", 100.0, 99.90, fee_bps_per_side=0.0)
    assert fill.signed_return_bps == pytest.approx(10.0)
    assert fill.net_pnl == pytest.approx(0.10)


def test_paper_fill_rejects_invalid_prices_and_quantity():
    with pytest.raises(ValueError):
        simulate_fill("LONG", 0.0, 100.0)
    with pytest.raises(ValueError):
        simulate_fill("LONG", 100.0, 100.0, quantity=0.0)
