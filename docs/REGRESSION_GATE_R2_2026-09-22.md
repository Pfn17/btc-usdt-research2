# Regression Gate R2 — 2026-09-22

**Run ID:** `FORENSIC-GATE-2026-09-22-R2`

## Purpose

Gate R2 re-runs the existing forensic decision-path checks after H-BASIS1 historical provenance recovery. It does not create a hypothesis, alter a frozen parameter, or replace the current funding-basis RPC. Gate R1 remains historical evidence in `FORENSIC-GATE-2026-09-22`.

## Tests

| Test | Expected | Observed | Result |
|---|---|---|---|
| Synthetic known positive | PASS | PASS | PASS |
| Synthetic below cost | KILL | KILL | PASS |
| Synthetic leakage | REJECT | REJECT | PASS |
| Synthetic train-only edge failing OOS | KILL | KILL | PASS |
| Canonical H-MR1 replay | MATCH | MATCH | PASS |
| Canonical historical H-BASIS1 replay | MATCH | MATCH | PASS |

The four synthetic observations are the existing `HARNESS-2026-09-22` records. H-MR1 uses the existing canonical replay evidence from Gate R1. H-BASIS1 was independently replayed in this run from the exact historical script at commit `5146f6ab173fad888e23558234822627ce801a30` against the frozen dataset hash `3ce9038421d76c3bf077dc3f5e3261a25311670286cca3801d90f113be470d79` and cutoff `2026-09-10T18:16:03Z`.

## H-BASIS1 replay evidence

The replay returned the following primary 15-minute OOS values:

- `N = 156`
- gross mean: `-1.0956948753997517 bps`
- net mean: `-11.09569487539975 bps`
- stress mean: `-13.09569487539975 bps`
- net CI95: `[-13.526151211184727, -8.55302646754086] bps`
- convergence: `53 / 156 = 0.33974358974358976`
- convergence CI95: `[0.1987179487179487, 0.4807692307692308]`
- median time to convergence: `2.024983333333333 minutes`

These values match the immutable historical result `907bf0bb-9ed5-4456-94ce-cf8dda2b5e26` within exact floating-point comparison. The event rows also matched exactly. The canonical implementation is `scripts/analyze_hbasis1_mechanism.py`, function `build_events(horizon_min)`, from historical commit `5146f6ab173fad888e23558234822627ce801a30`.

The current RPC `research_funding_basis_scan_frozen` was not used for the historical replay and was not modified. Its prior mismatch evidence, `agreement=0: 7,412` and `agreement=1: 2,862`, remains preserved in the lineage record.

## Overall gate

**Overall R2: PASS.** All six required regression tests passed. This is a regression and provenance result only. It is not a trading promotion decision, does not reopen hypothesis generation, and does not change the negative or underpowered status of any historical research result.

Project state remains:

- **Research state:** `PAUSED — NO NEW HYPOTHESES`
- **Retuning:** forbidden
- **Historical evidence:** append-only
- **Trading authorization:** `OFF`
- **H-BASIS1 historical status:** `INCONCLUSIVE / UNDERPOWERED`
- **H-BASIS1 provenance:** `RESTORED`

## References

[1]: docs/REGRESSION_GATE_2026-09-22.md "Historical Regression Gate R1"
[2]: docs/H-BASIS1_PROVENANCE_RECOVERY_2026-09-22.md "H-BASIS1 Provenance Recovery Report"
[3]: docs/artifacts/H-BASIS1_HISTORICAL_REPLAY_2026-09-22.json "Exact H-BASIS1 historical replay artifact"

[1] [2] [3]
