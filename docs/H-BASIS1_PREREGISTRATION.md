# H-BASIS1 Frozen Preregistration v1

**Status at freeze:** `FROZEN / MECHANISM RESEARCH ONLY / OUTCOME NOT YET QUERIED`

**Hypothesis identity:** `H-BASIS1`

**Family:** `H-BASIS1_BASIS_CONVERGENCE`

**Protocol:** `H-BASIS1_MECHANISM_V1`

**Freeze timestamp:** `2026-09-21T20:27:00Z`

## Research question

When the observed BTCUSDT mark-to-index basis deviates materially from its recent local equilibrium, does the deviation converge quickly and consistently enough to create a cost-adjusted trading opportunity? Convergence is treated as a measurable mechanism, not as evidence of executable profit.

The mark price and index price are both reference values. Neither is treated as a directly executable bid or ask. Any price-return calculation using `mark_price` is therefore a **non-executable proxy** and cannot by itself qualify H-BASIS1 for promotion or live trading.

## Data boundary

The only source for H-BASIS1 v1 is `public.funding_basis_snapshots` for `symbol='BTCUSDT'`. The observed frozen coverage is:

- First snapshot: `2026-09-03T04:34:56Z` (`server_time_ms=1788410096000`).
- Last snapshot: `2026-09-10T18:16:03Z` (`server_time_ms=1789064163000`).
- Observed rows: `10,510`.
- Distinct `server_time_ms` values: `10,510`.
- Invalid or null mark/index prices: `0` rows.
- Null generated `basis_bps`: `0` rows.

The final dataset hash is recorded only after the raw rows are downloaded in canonical order and before any event-level outcome is calculated.

The train/OOS calendar split is frozen before outcome access:

- **Train/discovery:** `2026-09-03T04:34:56Z` through `2026-09-07T23:59:59.999Z`.
- **OOS mechanism holdout:** `2026-09-08T00:00:00Z` through `2026-09-10T18:16:03Z`.
- No earlier H-MR1, H-VOL1, H-SW1, H-FB1, H-FB2, or H-FB3 OOS result is reused as H-BASIS1 evidence.

## Frozen feature and baseline

The stored generated field is:

```text
basis_bps = (mark_price / index_price - 1) * 10,000
```

For every snapshot at time `t`, define the local baseline as the median `basis_bps` of the prior six elapsed hours:

```text
baseline_6h(t) = median(basis_bps[u])
                   for t - 6 hours <= u < t
```

A baseline is valid only when at least 30 prior snapshots are available. The residual is:

```text
residual_bps(t) = basis_bps(t) - baseline_6h(t)
```

The six-hour baseline is the sole H-BASIS1 v1 baseline. One-hour, 24-hour, zero-centered, and alternative robust baselines are not silently substituted; testing any of them requires a new hypothesis identity.

## Frozen signal and event construction

The primary signal is an extreme residual relative to the train-only residual distribution:

```text
threshold = 90th percentile of abs(residual_bps)
            over valid TRAIN snapshots only
```

A snapshot is a candidate when:

```text
abs(residual_bps(t)) >= threshold
```

The signal side is defined only for a directional proxy:

- Positive residual: mark is above its local basis equilibrium; proxy direction is `SHORT`.
- Negative residual: mark is below its local basis equilibrium; proxy direction is `LONG`.

The signal snapshot itself is not used as the entry price. Entry is the first later observed snapshot with `server_time_ms >= signal_time + 60,000 ms`. This prevents same-snapshot leakage and avoids assuming a one-minute cadence that the data does not have.

The primary holding horizon is **15 minutes**. Sensitivity horizons are fixed in advance at **5, 30, and 60 minutes**. These sensitivity cells are descriptive robustness checks, not permission to select the best horizon after viewing results.

For a horizon `h`, the exit is the first observed snapshot with:

```text
server_time_ms >= entry_time + h
and server_time_ms <= entry_time + h + 120,000 ms
```

If no such snapshot exists, the event is censored for that horizon and is not assigned a fabricated exit price. The two-minute tolerance is frozen because the observed median interval is approximately one minute and the data contains longer gaps.

Events are accepted greedily in chronological order. After an event is accepted, the next candidate signal must occur after the accepted event's scheduled exit timestamp. This prevents overlapping event labels from being counted as independent observations. Signals without a valid entry or exit remain recorded as unavailable/censored diagnostics and do not become trades.

## Frozen convergence definitions

For each accepted event, compute the residual at entry and at the horizon exit using the same six-hour baseline rule, provided the baseline is valid at both timestamps.

A **50% convergence event** occurs when:

```text
abs(residual_exit_bps) <= 0.50 * abs(residual_entry_bps)
```

A **full sign-crossing event** occurs when:

```text
sign(residual_exit_bps) != sign(residual_entry_bps)
```

A convergence event is not declared when the exit baseline is unavailable. Such events are censored rather than imputed.

Time-to-convergence is the first observed timestamp after entry and before the primary 15-minute horizon at which the 50% convergence condition is met. If it is not met, the event is right-censored at the horizon. Overshoot is the maximum absolute residual after entry and before the horizon divided by the absolute entry residual. The directional proxy's adverse excursion is the maximum mark-price loss against the frozen proxy direction over the same interval.

## Frozen economic proxy

The project cost model is fixed:

- Fee: `4 bps per side`.
- Slippage: `1 bps per side`.
- Baseline round trip: `10 bps`.
- Stress round trip: `12 bps`.

The mark-price proxy returns are:

```text
LONG  = (exit_mark / entry_mark - 1) * 10,000
SHORT = (entry_mark / exit_mark - 1) * 10,000
```

The proxy net returns are:

```text
net_10bps    = gross_proxy_bps - 10
stress_12bps = gross_proxy_bps - 12
```

These values are **not executable P&L** because the dataset has no bid/ask fills, order-book impact, or guaranteed mark-to-trade execution equivalence. They are reported only to answer whether the observed convergence magnitude is even large enough to clear the project's fixed cost hurdle.

## Statistical and calendar rules

The primary reporting unit is the accepted non-overlapping event. Calendar consistency is reported by UTC day blocks and by the frozen train/OOS periods. No random split is permitted.

The primary confidence interval for the OOS proxy mean uses a moving block bootstrap over UTC-day event blocks with:

- block size: `1 calendar day`;
- bootstrap samples: `2,000`;
- seed: `20260921`;
- percentile interval: empirical `2.5%` to `97.5%`;
- sensitivity blocks: `12 hours` and `48 hours`, reported without selecting a winner.

The mechanism study reports raw sample size and unique active UTC-day blocks separately. Raw snapshots are not treated as independent observations.

## Predeclared interpretation gates

H-BASIS1 v1 is **not a promotion test**. It can produce only the following mechanism-stage states:

- `MECHANISM_SUPPORTED`: OOS 50% convergence rate exceeds 50%, the primary OOS convergence CI excludes zero in the positive direction, and no unresolved continuity issue remains.
- `MECHANISM_WEAK`: convergence is observed but the OOS confidence interval crosses zero, event count or active-day count is small, or the result is concentrated in one day.
- `MECHANISM_REJECTED`: OOS convergence is not positive or the residual does not show persistence/convergence beyond the frozen definition.
- `UNDERPOWERED`: fewer than 30 accepted OOS events or fewer than 5 active OOS UTC days.

Even `MECHANISM_SUPPORTED` does not mean `PASS`, `PROMOTION`, or `PRODUCTION READY`. A separate frozen directional economic hypothesis and an independent verifier would be required. Any economic proxy with a net CI crossing zero, non-positive stress mean, unresolved data gap, or mark/execution mismatch is not a promotion candidate.

## Data-quality rules

Snapshot cadence is evaluated from actual `server_time_ms`, not row count. Gaps are reported and never bridged. The observed initial audit found a median interval near one minute, `12` gaps greater than five minutes, and a maximum interval near 32 minutes. Any event whose entry, exit, or convergence measurement crosses an unavailable timestamp is censored under the rules above.

## Multiple-testing and lineage

H-BASIS1 is a new mechanism identity. It is not a retuning of H-FB1 or H-FB2 because it studies local mark-to-index basis residual convergence rather than funding-sign direction or funding-event carry. It is also not a reuse of H-SW1, H-MR1, H-VOL1, Family D, or H-FB3. The finite sensitivity cells are declared before results and are not individually promoted. Any follow-up baseline, threshold, horizon, or execution definition requires a new hypothesis key and a new preregistration.

## Execution boundary

No order path is introduced or enabled. H-BASIS1 is read-only research. Trading authorization remains `OFF`.

## Freeze metadata

- Specification hash: `f9b3c6cefc7986c6785d2cb4c3434ba6fb834a888ad7bf8fbf3f6d324198c08e`.
- Dataset hash: `3ce9038421d76c3bf077dc3f5e3261a25311670286cca3801d90f113be470d79`.
- Query cutoff: the dataset's last observed `server_time_ms`, `2026-09-10T18:16:03Z`.
- Raw snapshot extraction and hashes were completed before event-level mechanism calculations.
- Outcome status at freeze: `NOT QUERIED`; the mechanism calculation uses only this frozen specification and frozen dataset boundary.
