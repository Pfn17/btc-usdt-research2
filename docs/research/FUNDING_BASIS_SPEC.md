# Funding/Basis Family — Preregistered Research Specification

## Objective
Test whether perpetual funding and basis state contain a repeatable predictive edge after realistic execution costs.

## Status
BUILT / UNVALIDATED. No evidence of profitability is assumed.

## Data
- Binance public USDⓈ-M futures funding history (`/fapi/v1/fundingRate`)
- Binance public premium index (`/fapi/v1/premiumIndex`)
- BTCUSDT perpetual/index/mark information where available
- Existing OHLCV may be used only as a frozen conditioning/context variable; it is not swept.

## Frozen signals
1. Funding level: signed funding rate at the latest completed funding observation.
2. Funding change: first difference between consecutive completed funding observations.
3. Basis: signed mark-vs-index premium, normalized to basis points.
4. Basis change: first difference of the normalized basis.
5. Joint direction: funding and basis agree/disagree.

No arbitrary threshold grid search is permitted in this family.

## First frozen evaluation
- Signal observation: latest completed funding observation plus contemporaneous premium-index snapshot.
- Forward label horizon: **240 minutes (4 hours)**.
- Sampling cadence: one research observation per funding/basis snapshot; duplicate server timestamps are excluded by the unique key.
- Temporal evaluation: walk-forward/OOS with purge and embargo using the repository's existing research protocol.

The 240-minute horizon is frozen before inspecting funding/basis performance. It is deliberately longer than the 5–60 minute latency-sensitive tests used for microstructure because funding is an 8-hour periodic structural variable and basis is a slower state variable. This is a single test, not a horizon sweep.

## Evaluation
Use only observations available at signal time. Future returns are labels only. Use temporal walk-forward/OOS evaluation with purge and embargo. Report gross EV, fees, spread/slippage assumptions, net EV, sample size, win rate and confidence intervals. Confidence intervals used for acceptance must correspond to net returns after costs.

## Cost models
At minimum evaluate the existing base cost model and a conservative stress model. A positive gross result is never sufficient for acceptance.

## Acceptance
PASS only if positive net EV is independently reproducible across multiple temporal OOS folds, survives conservative costs, has adequate sample size, and is not concentrated in one isolated regime. Otherwise KILL.

## Execution role
L2/microstructure remains timing/execution context only and is not part of the predictive family.

## Live trading
Disabled. This family cannot enable live trading without independent paper validation and explicit live gate approval.
