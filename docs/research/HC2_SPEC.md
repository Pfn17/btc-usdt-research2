# H-C2 — OHLCV-Only Conditional Edge

## Objective
Find a repeatable short-horizon BTCUSDT perpetual edge whose expected value remains positive after fees, spread, slippage and realistic execution costs.

## Family decision
The microstructure signal family is KILLED. Order-book imbalance, microprice, order-flow and depth variables must not be used as predictive signal features. They may be used later for timing, execution quality, liquidity checks and monitoring only.

## Frozen hypothesis
Short-horizon BTCUSDT directional returns contain repeatable conditional information in OHLCV state: recent returns/momentum, candle range, realized volatility, volume and volume regime. The research must determine whether any OHLCV state has positive net EV after costs.

## Signal features
Allowed predictive inputs are OHLCV-derived only:
- 1m returns and multi-minute returns
- candle range / true range
- realized volatility
- volume and volume change
- quote volume
- trade count
- taker-buy volume ratio
- rolling high/low position and breakout distance

Explicitly excluded from signal generation:
- order-book imbalance
- microprice
- depth
- order-flow imbalance
- spread as a predictive feature

## Horizons
5m, 15m, 30m, 60m, 120m and 240m. Horizon is frozen before each experiment batch.

## Rules
1. Every signal feature must be computable using information available at the decision timestamp.
2. Future OHLCV values are labels only and never predictors.
3. No random train/test split.
4. Use temporal walk-forward evaluation with purge and embargo.
5. Thresholds are selected on train data only.
6. Report gross EV and cost-adjusted net EV separately.
7. Net EV must subtract fees and conservative slippage; execution assumptions must be explicit.
8. Reject candidates whose positive EV depends on one fold, one regime or one narrow period.
9. Apply multiple-testing/FDR controls when searching multiple OHLCV hypotheses.
10. Microstructure can only enter after signal generation as timing/execution context.

## Acceptance gate
PAPER_CANDIDATE requires positive OOS net EV, positive lower confidence bound, multiple positive temporal folds, sufficient sample size, no leakage, regime stability and cost-stress survival.

## Live gate
LIVE_CANDIDATE requires independent reproduction, paper-trading confirmation, execution monitoring, persistent audit coverage, kill-switches and explicit human approval. H-C2 never enables live trading automatically.
