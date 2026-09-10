# H-FB3 Frozen Preregistration — Closed-Range Directional Expansion Continuation

## Status

**FROZEN — one discovery run and one untouched out-of-sample validation.** This document is a preregistration of the H-FB3 test, not evidence of profitability. No order execution is enabled.

The hypothesis remains **ALIVE** while Stage 2 is locked until this freeze is independently reconciled and verified.

## Mechanism

A fully closed one-minute candle with unusually large range and a close near its directional extreme may indicate short-term continuation rather than immediate reversal. The test uses existing BTCUSDT 1m OHLCV only.

This mechanism is materially distinct from the previously tested funding-crowding family, Family D momentum variants, and H-SW1 swing lineage. No prior family may be silently reused or inverted.

## Frozen signal definition

For each completed 1m candle `t`:

- `range_bps = 10000 * (high_t - low_t) / open_t`
- `close_location = (close_t - low_t) / (high_t - low_t)`
- eligible range: `range_bps >= 8`
- LONG signal: `close_location >= 0.80`
- SHORT signal: `close_location <= 0.20`
- no signal when `high_t == low_t` or the directional conditions are not met

The signal is evaluated only after candle `t` is complete.

### Entry and exit

- **Entry:** open of the next 1m candle.
- **Holding horizon:** 5 minutes.
- **Exit:** close of the fifth held 1m candle after entry.
- **LONG return:** `(exit_price / entry_price - 1) * 10000`.
- **SHORT return:** `(entry_price / exit_price - 1) * 10000`.
- No alternative signed-return formula is considered equivalent for this preregistration.

### Non-overlap rule

Accept the earliest eligible signal. Suppress any later signal whose entry occurs before the scheduled exit of the previously accepted signal. This produces a non-overlapping OOS signal sample.

## Temporal split

- **Discovery/train period:** first 60 calendar days.
- **OOS period:** remaining complete calendar days after the discovery period.
- All timestamps are UTC.
- No random split is permitted.
- No OOS observation may influence the frozen rule before evaluation.

### Frozen dataset cutoff metadata

- Dataset table: `public.ohlcv_1m`
- Canonical fields: `symbol interval open_time_ms close_time_ms open high low close volume quote_volume trade_count taker_buy_volume taker_buy_quote_volume`
- `collected_at` is excluded from the canonical dataset.
- Row count: **141,295**
- First `open_time_ms`: **1780552860000** = `2026-06-04T06:01:00Z`
- Last `open_time_ms`: **1789035480000** = `2026-09-10T10:18:00Z`
- Train start: `2026-06-04T00:00:00Z`
- Train end: `2026-08-02T23:59:59.999Z`
- OOS start: `2026-08-03T00:00:00Z`
- OOS complete-day end: `2026-09-09T23:59:59.999Z`
- Query cutoff: `2026-09-10T10:18:00Z`

The canonical dataset freeze is UTF-8 NDJSON, ascending `open_time_ms`, exact database numeric text representation, frozen field order, and a final newline.

- **Dataset SHA-256:** `fc50dad316294d51f4dcde2a1d08b6450d4561cd2d9353717f1f7bfe2b215947`
- **Specification SHA-256:** `d30dc52492e5b84c2d0cf1cddededc2b1414a5a3649ace226ba092d7b0208b6d`

The specification hash identifies the frozen test parameters; it is not a performance result.

## Cost model

### Baseline

- Fee: **4 bps per side**
- Slippage: **1 bps per side**
- Total round-trip cost: **10 bps**
- `net_bps = gross_bps - 10`

### Stress

- Total round-trip cost: **12 bps**
- `net_bps_stress = gross_bps - 12`

No post-outcome cost reduction or alternative fee/slippage assumption is permitted.

## Latency assumption

The signal is based only on a completed candle. Entry is the next candle open, representing a one-full-candle delay from signal observation to entry. No future candle value may enter the signal definition.

## Statistical evaluation

The primary confidence interval uses the repository's existing `evaluate_predictions()` convention:

1. arithmetic mean of the OOS net-return sample;
2. sample variance;
3. standard error of the mean;
4. two-sided 95% normal-approximation interval: `mean +/- 1.96 * SE`.

The frozen rule is not replaced by bootstrap, Bayesian intervals, or another estimator after the outcome is seen.

## Mandatory OOS acceptance gate

All conditions below must hold for H-FB3 to pass:

1. Combined OOS net mean is **greater than 0 bps**.
2. Combined OOS 95% CI lower bound is **greater than 0 bps**.
3. At least **30 retained, non-overlapping OOS signals** are available.
4. At least **4 complete OOS ISO weeks** are observed.
5. At least **3 of the first 4 observed complete OOS ISO weeks are positive**.
6. No single ISO week contributes more than **50% of total positive OOS net profit**.
7. Stress-cost net mean remains **positive** at 12 bps round-trip cost.
8. At least **10 LONG** and **10 SHORT** retained OOS signals are available.
9. LONG mean net return is positive.
10. SHORT mean net return is positive.
11. The combined OOS CI gate in item 2 remains satisfied.

For weekly concentration, an empty week is neither positive nor negative. Fewer than 4 observed complete OOS weeks is **DATA_INSUFFICIENT**, not a pass.

Failure of any mandatory gate is a **KILL** of H-FB3. No threshold, direction, horizon, filter, split, cost model, latency assumption, CI method, or acceptance gate may be changed after inspecting the OOS outcome.

## Multiple-testing boundary

H-FB3 is not retrospectively adjusted with a new FDR/BH correction after seeing its outcome. Any project-wide multiple-testing policy must be decided and frozen before H-FB3 outcome evaluation if it is to be applied to this experiment family.

## Paper-trading boundary

Only a passing OOS result may proceed to paper validation. Paper validation remains read-only with respect to exchange execution and must not contain API-key-based order placement.

## Execution lock

Until the frozen artifact is independently reconciled and verified, **Stage 2 outcome/backtest execution is LOCKED**. No outcome query, parameter sweep, migration, RPC change, infrastructure change, or dashboard change is part of this preregistration.

## Audit / provenance

The preregistration was prepared from the owner-approved H-FB3 candidate and reviewed for formula correctness, data sufficiency, sample-size limitations, and multiple-testing concerns before outcome evaluation.

The original executor artifact was reported as commit `e51c4f57600bb022374303dcfda33e0e16ff04e4`. Repository reconciliation must establish an observable shared-repository commit before the freeze is treated as independently verified. No rollback, deletion, amendment, or replacement of that reported artifact is authorized by this document.
