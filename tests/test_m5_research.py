import math

from btc_research.research import (
    CostModel, ExperimentFamily, Hypothesis, LogisticModel, ResearchFreeze,
    StandardScaler, benjamini_hochberg, block_bootstrap_mean, evaluate_predictions,
    generate_walk_forward_splits, paired_differences, triple_barrier_label, uniqueness_weights,
)


def test_hypothesis_freeze_has_stable_fingerprint() -> None:
    family = ExperimentFamily("fam-1", "microstructure")
    h = Hypothesis.create("H-001", family.family_id, "imbalance predicts 60s return", 60, "two_sided")
    freeze = ResearchFreeze.create("F-001", family.family_id, {"pt": 0.001, "sl": 0.001, "horizon_ms": 60_000})
    assert h.family_id == family.family_id
    assert len(freeze.fingerprint) == 64


def test_triple_barrier_label_uses_only_future_observations() -> None:
    result = triple_barrier_label(1_000, 100.0, [1_100, 1_200], [100.2, 101.0], 0.005, 0.005, 500)
    assert result.label == 1
    assert result.reason == "take_profit"


def test_walk_forward_has_purge_gap_and_embargo() -> None:
    splits = generate_walk_forward_splits(list(range(0, 100, 10)), 30, 20, 10, 10, 20)
    assert splits[0].train_end_ms == 30
    assert splits[0].test_start_ms == 40
    assert splits[0].test_end_ms == 60


def test_scaler_and_logistic_model_are_deterministic() -> None:
    x = [[-2.0], [-1.0], [1.0], [2.0]]
    y = [-1, -1, 1, 1]
    scaler = StandardScaler.fit(x)
    model = LogisticModel.fit(scaler.transform(x), y, epochs=200, learning_rate=0.1)
    assert model.predict(scaler.transform(x)) == y


def test_costs_and_paired_results() -> None:
    costs = CostModel(fee_bps=2, half_spread_bps=1, slippage_bps=1)
    assert math.isclose(costs.round_trip_bps, 8)
    assert paired_differences([0.02, 0.01], [0.01, 0.02]) == [0.01, -0.01]
    result = evaluate_predictions([0.01, -0.005, 0.002])
    assert result.n == 3
    assert result.ci95_low <= result.mean_return <= result.ci95_high


def test_robustness_helpers() -> None:
    bootstrap = block_bootstrap_mean([0.0, 0.01, -0.01, 0.02] * 5, block_size=2, samples=100, seed=7)
    assert bootstrap.samples == 100
    assert len(benjamini_hochberg([0.001, 0.02, 0.9])) == 3
    assert uniqueness_weights([(0, 10), (5, 15), (20, 30)]) == [0.5, 0.5, 1.0]
