# H-VOL1 Preregistration — Breakout Confirmed by Extreme Taker-Flow Participation

## Status

**METHODOLOGY FROZEN / IMPLEMENTED / READINESS VISIBLE / OUTCOME UNRUN.** This document is a specification and readiness contract, not evidence of profitability. No H-VOL1 outcome or OOS profitability scan is authorized by this implementation. Trading and paper promotion remain disabled.

## Research question

Does a 120-minute BTCUSDT price breakout have better continuation when the breakout candle is accompanied by extreme directional taker-buy participation? The predictive input is the OHLCV-derived `taker_buy_volume / volume` ratio. This is a new hypothesis identity and is not a generic volume claim.

## Frozen signal definition

Use closed `public.ohlcv_1m` candles. For breakout candle `t`, define the prior range from the preceding **120 actual elapsed minutes**, excluding `t`:

- `prior_high[t] = max(high)` over timestamps `t - 120 minutes` through `t - 1 minute`;
- `prior_low[t] = min(low)` over the same interval.

A range window is valid only when all 120 expected one-minute timestamps exist. Missing candles must invalidate the window; the implementation must not use nearest-candle substitution, forward fill, interpolation, row-count substitution, or silent gap bridging.

An upside breakout requires `close[t] > prior_high[t]`. A downside breakout requires `close[t] < prior_low[t]`. Equality is not a breakout.

For candles with `volume > 0`, define `taker_buy_ratio = taker_buy_volume / volume`. Candles with `volume <= 0` are invalid and excluded from the percentile population. Training-only thresholds are:

- upside confirmation: `P90(taker_buy_ratio)`;
- downside confirmation: `P10(taker_buy_ratio)`.

The thresholds are calculated only from the chronological training segment and must be frozen before any OOS outcome is observed. Confirmed upside breakouts produce `LONG`; confirmed downside breakouts produce `SHORT`. An unconfirmed breakout produces no entry.

## Entry, exit, and non-overlap

Entry is the open of candle `t + 1 minute`. Exit is the close of the candle exactly **120 elapsed minutes after entry**. If either exact timestamp is absent, the candidate is rejected; the implementation must not silently substitute the next available candle.

Candidates are ordered chronologically. Greedy non-overlap is based on the previous **accepted trade's scheduled exit**, not the previous raw candidate's exit. The selection is deterministic.

## Cost and statistics contract

Baseline cost is the project convention of 4 bps fee per side plus 1 bps slippage per side: **10 bps round trip**. Stress cost is **12 bps round trip**. The eventual outcome function returns overall, ISO-week, and direction breakdowns; arithmetic-mean normal-approximation CI95; baseline and stress economics; weekly positive-count and concentration checks; and the promotion/kill/inconclusive gate fields used by H-FB3/H-MR1.

The H-VOL1 result must be entered into the project-wide hypothesis/FDR ledger if and only if an authorized outcome scan is later run. FDR cannot rescue a failed economic or confidence gate.

## OOS boundary and authorization

The exact OOS boundary is intentionally **NOT YET FROZEN** in this implementation. The readiness API accepts an explicit boundary only to calculate factual training/OOS readiness; the dashboard does not invent or submit one. Until a boundary is independently reviewed, explicitly recorded, and authorized:

- outcome status is **UNRUN**;
- OOS outcome observed is **NO**;
- authorization is **NOT GRANTED**;
- the dashboard must not preview profitability;
- no H-VOL1 scan may be called by the dashboard.

## Readiness surface

`GET /api/v1/research/hvol1/readiness` is the only dashboard-facing H-VOL1 endpoint. It reports backend-derived facts including coverage, one-minute gaps, complete 120-minute range-window availability, valid ratio observations, train/OOS counts, train P90/P10 when an explicitly supplied boundary exists, exact entry/exit availability, non-overlap methodology, baseline/stress costs, boundary state, outcome state, and authorization state. Uncomputed or unfrozen values remain `NOT FROZEN`, `NOT YET COMPUTED`, or `UNAVAILABLE`.

`GET /api/v1/research/hvol1` remains manual and research-only for a future authorized run. It is not polled by the dashboard and does not enable execution.

## Audit boundary

This implementation must leave an append-only trail stating:

- H-VOL1 outcome scan: **NOT RUN**;
- OOS outcome observed: **NO**;
- authorization: **NOT GRANTED**;
- status: **AWAITING INDEPENDENT AUDIT**.

An independent verifier must review the source migration, live RPC identity, readiness payload, API route, dashboard rendering, and test suite before any cutoff is frozen or any outcome is executed.
