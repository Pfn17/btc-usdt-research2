# H-MR1 Gate Specification

**Status:** FROZEN IMPLEMENTED · METHOD NOT READY · OUTCOME UNRUN · AUTHORIZATION NOT GRANTED · TRADING DISABLED

H-MR1 tests whether an extreme closed 15-minute BTCUSDT move, defined by the train-only 95th percentile of absolute return, predicts partial reversal over the next one hour. The specification is registered in Supabase under `H-MR1`. This document records the gate implementation; it does not record an outcome.

## Exact trigger predecessor

A trigger at candle time `t` is eligible only when the BTCUSDT 1-minute candle at exactly `t - 15 minutes` exists. The implementation uses an exact timestamp join. It does not use row offset, nearest-candle lookup, fill, interpolation, or bridging across a gap.

## Entry and exit availability

The entry is the first available 1-minute open at or after `trigger + 1 minute`, within the frozen one-hour alignment tolerance. The exit is the first available 1-minute close at or after `entry + 60 minutes`, within the frozen one-hour alignment tolerance. A candidate without both fills is excluded from the candidate set and is visible through the separate readiness facts.

## Greedy chronological non-overlap

Filled candidates are ordered chronologically by entry timestamp and trigger timestamp. The first valid candidate is accepted. The next accepted candidate is the first candidate whose entry timestamp is at or after the previously accepted trade's scheduled exit. Candidates that overlap are rejected while the chronological search continues. This is implemented by a recursive CTE; a window `lag(exit)` filter is not used.

## Readiness-only RPC

`research_hmr1_readiness(p_as_of_ms, p_oos_start_ms)` reports backend-derived facts only:

- coverage start and end;
- observed candle count and expected minute count;
- missing-minute count and continuity state;
- exact predecessor count and rate;
- entry and exit availability counts;
- training and OOS candle coverage;
- complete OOS ISO-week count;
- whether the OOS boundary is frozen;
- whether an outcome was run.

The RPC always reports `outcome_run = false`. The API route `/api/v1/research/hmr1/readiness` never calls the outcome RPC.

## OOS boundary

The exact UTC cutoff and `p_oos_start_ms` are intentionally **not frozen yet**. No agent may choose, infer, or display a substitute cutoff. Until the owner explicitly approves the exact boundary, readiness must remain `NOT_READY`, no H-MR1 scan may be called, and no performance number may be displayed as an H-MR1 result.

## Dashboard contract

The Terminal page displays the readiness state, coverage/continuity, exact predecessor evidence, entry/exit availability, training/OOS counts, complete ISO weeks, OOS boundary state, and outcome state. `UNAVAILABLE` is shown when the backend cannot provide a fact. No placeholder, mock, or fabricated value is allowed.
