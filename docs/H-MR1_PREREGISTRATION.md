# H-MR1 Preregistration — Intraday Extreme-Candle Mean Reversion

## Status

**Frozen for one discovery/OOS evaluation path. No outcome scan has been run by this implementation.** This document is a specification, not evidence of profitability. No order execution or paper promotion is enabled.

## Mechanism

H-MR1 tests whether an extreme closed 15-minute move in BTCUSDT is more likely to partially reverse than continue. This is a new reversal mechanism, distinct from the project's prior continuation/momentum families.

## Frozen signal definition

Using only closed `ohlcv_1m` candles, define a candidate at minute `t` from the trailing 15-minute close-to-close return ending at `t`:

`return_15m_bps = 10,000 * (close_t / close_(t-15) - 1)`

The absolute-return threshold is the **95th percentile calculated only from the chronological training segment**. The threshold is frozen before OOS scoring. A candidate triggers when `abs(return_15m_bps) >= threshold_bps`; its direction is the opposite of the trigger (`SHORT` after an upward extreme, `LONG` after a downward extreme).

Entry is the first available open price at or after the next one-minute candle (`t + 1 minute`). Exit is the first available close at or after `entry + 60 minutes`, with a one-hour horizon tolerance of one hour for missing-candle alignment. Candidates are selected chronologically and the next candidate must be at or after the previous scheduled exit, enforcing non-overlap.

## Temporal split

The OOS boundary is an explicit frozen `p_oos_start_ms` supplied to the scan. Training uses only candidates whose trigger closes before that boundary. OOS uses candidates whose trigger closes at or after that boundary. The recommended run uses the final six complete ISO weeks as OOS, but the exact cutoff must be recorded before execution. No random split, threshold retuning, or post-outcome cutoff adjustment is allowed.

## Cost model and statistics

Baseline cost is 4 bps fee per side plus 1 bps slippage per side: **10 bps round trip**. Stress cost is **12 bps round trip**. The RPC returns gross bps, baseline net bps, stress net bps, normal-approximation CI95 for both net series, win rate, and temporal buckets. It reports overall, ISO-week, and direction breakdowns.

## Gates

Promotion requires all of the following: baseline net mean greater than zero; baseline CI95 lower bound greater than zero; at least six complete OOS ISO weeks; a majority of OOS weeks positive; stress net mean greater than zero; stress CI95 lower bound greater than zero; and no single week contributing more than half of total positive net contribution. If any mandatory condition fails, H-MR1 is **KILL**. If the effective OOS sample is too small for the predeclared six-week and confidence requirements, it is **INCONCLUSIVE**, not PASS.

No H-MR1 outcome is inferred from the existence of this migration or API route.

## Multiple-testing note

H-MR1 receives its own hypothesis identity. Its result must be added to the project-wide hypothesis ledger for future multiple-testing/FDR accounting. It must not be represented as confirmation of H-FB1, H-FB3, H-SW1, or any other family.

## Execution boundary

The migration is read-only and `SECURITY DEFINER` with restricted execution grants. The API route is research-only and manual. No Binance order endpoint, API-key order path, or paper promotion is introduced.

## Frozen implementation lineage

- Migration: `20260911090000_hmr1_extreme_mean_reversion.sql`
- API route: `/api/v1/research/hmr1`
- Expected initial state: **UNRUN / no outcome**
- Implementer: Manus

A separate independent verifier must inspect the migration and API before any outcome scan is executed.
