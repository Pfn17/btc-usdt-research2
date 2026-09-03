from btc_research.hc2 import build_hc2_state, imbalance, microprice


def test_imbalance_is_bounded():
    assert imbalance(75, 25) == 0.5
    assert imbalance(25, 75) == -0.5


def test_microprice_weights_opposite_side_depth():
    value = microprice(100, 99, 101, 75, 25)
    assert value == 99.5


def test_hc2_state_has_no_future_label():
    state = build_hc2_state(
        return_5s=0.001,
        return_15s=0.002,
        return_30s=0.003,
        rv_30s=0.01,
        volume_z=1.2,
        volume_accel=0.3,
        mid=100,
        bid=99.99,
        ask=100.01,
        bid_depth=75,
        ask_depth=25,
        signed_flow=20,
        total_flow=40,
    )
    assert state is not None
    assert state.book_imbalance == 0.5
    assert state.order_flow_imbalance == 0.5
    assert state.flow_agreement == 1.0
