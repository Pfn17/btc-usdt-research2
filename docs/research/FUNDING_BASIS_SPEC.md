# Funding/Basis Family — Preregistered Research Specification

## Objective
Test whether the sign of completed perpetual funding contains a repeatable predictive edge after realistic execution costs.

## Status
BUILT / UNVALIDATED. No profitability is assumed.

## Data
- Binance public USDⓈ-M futures funding history (`/fapi/v1/fundingRate`)
- Binance public premium index (`/fapi/v1/premiumIndex`) for contemporaneous mark/index context
- Existing OHLCV may be used only as frozen context; it is not swept.

## First frozen hypothesis — H-FB1
**Signal:** sign of `last_funding_rate` at a completed funding event.

- Positive funding = long-side funding signal.
- Negative funding = short-side funding signal.
- Zero funding = no directional signal and excluded from the directional EV test.
- No magnitude threshold is introduced.
- No funding-delta, basis-delta, agreement, or other derived signal is included in batch 1.

**Forward label:** 240 minutes (4 hours) after the completed funding observation.

**Sampling:** one observation per completed funding event. Intraday premium-index snapshots are not treated as independent research observations for H-FB1.

**Evaluation:** temporal walk-forward/OOS with purge/embargo using the repository research protocol. The cutoff and fold definitions are frozen before evaluation.

This is one hypothesis and one horizon, not a horizon or threshold sweep. If H-FB1 fails, any additional funding/basis hypothesis requires a separate written rationale and preregistration before testing.

## Costs and acceptance
Report gross EV, fees, spread/slippage assumptions, **net EV**, sample size, win rate and confidence intervals. Acceptance CIs must be calculated on net returns after costs. Evaluate the existing base cost model and a conservative stress model.

PASS only if positive net EV is independently reproducible across multiple temporal OOS folds, survives conservative costs, has adequate sample size, and is not concentrated in one isolated regime. Otherwise KILL.

## Execution role
L2/microstructure remains timing/execution context only and is not part of the predictive family.

## Live trading
Disabled. This family cannot enable live trading without independent paper validation and explicit live gate approval.
