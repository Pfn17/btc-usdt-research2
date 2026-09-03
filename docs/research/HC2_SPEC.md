# H-C2 — Conditional Microstructure × OHLCV Edge

## Objective
Find a repeatable short-horizon BTCUSDT perpetual edge whose expected value remains positive after spread, fees, slippage and adverse-selection allowance.

## Frozen hypothesis
Microstructure imbalance has predictive value only when conditioned on the joint market state: short-horizon OHLCV momentum/reversal, realized volatility, spread/liquidity and order-flow agreement.

## Horizons
5s, 15s, 30s, 60s, 120s. Horizons are frozen before evaluation.

## Candidate state variables
- order-book imbalance at available depth levels
- microprice deviation from mid
- bid/ask spread in bps
- bid/ask depth and depth imbalance
- signed trade/order-flow imbalance
- short-horizon return and candle range
- realized volatility
- volume and volume acceleration

## Rules
1. Features must use information available at signal timestamp only.
2. Labels use future mid/mark-price movement only after the signal timestamp.
3. No random train/test split.
4. Use temporal walk-forward evaluation with purge and embargo.
5. No threshold optimization on OOS data.
6. Every experiment records hypothesis, feature set, horizon, split definition and cost model.
7. Report gross EV and net EV separately.
8. Net EV must subtract fees, spread crossing, slippage and an adverse-selection stress allowance.
9. A candidate is not a trading edge unless positive net EV survives OOS and cost stress tests.
10. This experiment cannot enable live trading by itself.

## Cost scenarios
Evaluate at minimum:
- optimistic: observed execution cost
- base: observed execution cost + conservative slippage
- stress: base cost multiplied by 1.5

## Acceptance gate
A candidate may become PAPER_CANDIDATE only when:
- OOS net EV > 0 in the base cost model;
- OOS net EV remains > 0 under stress or has a separately documented degradation boundary;
- positive performance is present across multiple temporal folds;
- sample size is sufficient for a stable confidence interval;
- no leakage or post-signal feature is detected;
- performance is not concentrated in one isolated regime;
- execution latency and liquidity constraints are compatible with the signal horizon.

## Live gate
LIVE_CANDIDATE requires independent reproduction, paper-trading confirmation, runtime audit coverage, kill-switches and explicit human approval. H-C2 implementation never sets trading_enabled=true.
