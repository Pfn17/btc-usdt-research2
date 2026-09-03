# Funding/Basis Family — Preregistered Research Specification

## Objective
Test whether the sign of completed perpetual funding contains a repeatable predictive edge after realistic execution costs.

## Status
BUILT / UNVALIDATED. No profitability is assumed.

## Data
- Binance public USDⓈ-M futures funding history (`/fapi/v1/fundingRate`)
- Binance public premium index (`/fapi/v1/premiumIndex`) for contemporaneous mark/index context
- Existing OHLCV may be used only as frozen context for the forward price label; it is not a signal sweep.

## First frozen hypothesis — H-FB1
**Signal:** sign of `last_funding_rate` at a completed funding event.

- Positive funding = long-side funding signal.
- Negative funding = short-side funding signal.
- Zero funding = no directional signal and excluded from the directional EV test.
- No magnitude threshold is introduced.
- No funding-delta, basis-delta, agreement, or other derived signal is included in batch 1.

**Forward label:** 240 minutes (4 hours) after the completed funding observation.

**Sampling:** one research observation per completed funding event, with a minimum 240-minute embargo between selected research observations so forward labels cannot overlap. Intraday premium-index snapshots are not research observations for H-FB1.

**Evaluation:** temporal OOS using a cutoff frozen before evaluation. The hypothesis has no fitted parameters, so the OOS test is a fixed-rule holdout rather than a parameter-optimization exercise. Any fold reporting must preserve the same rule and horizon.

## Frozen cost model
Base model: **4 bps fee per side + 1 bps slippage per side = 10 bps round-trip trading cost**. The RPC reports net return after this cost and computes the confidence interval on net returns. A conservative stress call may increase costs, but cannot change the signal or horizon.

## Acceptance
Report gross EV, net EV, sample size, win rate, and **net 95% confidence interval**, plus temporal OOS results. PASS only if positive net EV is independently reproducible across multiple temporal OOS periods, survives conservative cost stress, has adequate sample size, and is not concentrated in one isolated regime. Otherwise KILL.

This is one hypothesis and one horizon, not a horizon or threshold sweep. If H-FB1 fails, any additional funding/basis hypothesis requires a separate written rationale and preregistration before testing.

## Execution role
L2/microstructure remains timing/execution context only and is not part of the predictive family.

## Live trading
Disabled. This family cannot enable live trading without independent paper validation and explicit live gate approval.
