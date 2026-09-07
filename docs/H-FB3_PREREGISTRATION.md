# H-FB3 Preregistration — Closed-Range Momentum Continuation

## Status

**Frozen for one discovery run and one untouched out-of-sample validation.** This document is a specification, not evidence of profitability. No order execution is enabled.

## Mechanism

A large, fully closed one-minute candle that finishes near its directional extreme may indicate short-term continuation rather than immediate reversal. The mechanism is tested using OHLCV data only, so it does not depend on the rejected funding family or the rejected H-C1 L2 combination.

## Frozen signal definition

For each closed one-minute candle `t`, define:

- `range_bps = 10,000 * (high_t - low_t) / open_t`;
- `close_location = (close_t - low_t) / (high_t - low_t)`;
- LONG when `range_bps >= 8`, `close_location >= 0.80`, and the next candle is the entry observation;
- SHORT when `range_bps >= 8`, `close_location <= 0.20`, and the next candle is the entry observation;
- no signal when the candle range is zero or the conditions are not met.

The exit horizon is **5 minutes** after the entry observation. The return is signed according to direction. No threshold, direction, horizon, or filter may be changed after the OOS result is inspected.

## Dataset and temporal split

Use only `ohlcv_1m`, ordered by `open_time_ms`, with no random split. The first 60 days are the discovery period. The remaining available days are untouched OOS validation. The OOS cutoff must be recorded before the query is executed. Candle `t` must be closed before its signal is evaluated, and the entry must not use any future candle value.

## Cost and acceptance gate

The baseline cost is **4 bps fee per side plus 1 bps slippage per side**, or 10 bps round trip. The reported net return is gross signed return minus 10 bps. A candidate is promoted only if all conditions hold:

1. OOS net expectancy is greater than zero.
2. The two-sided 95% confidence interval lower bound is greater than zero.
3. Effective OOS sample size is at least 30 independent signals.
4. Results are not concentrated in a single calendar week.
5. The result remains positive under a 2 bps increase in round-trip cost.

Failure of any condition kills H-FB3. Retuning after failure is prohibited. A materially different mechanism must receive a new hypothesis ID.

## Paper-trading follow-up

Only a passing OOS result may enter paper validation. Paper fills must record signal time, entry observation, exit observation, direction, expected cost, realized signed return, net PnL, data quality, and contamination status. The simulated execution layer is read-only with respect to Binance and must not contain API-key-based order placement.
