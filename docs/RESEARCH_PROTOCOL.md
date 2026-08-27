# Research Protocol v1 — Foundation

## Objective
Determine whether BTCUSDT Futures contains repeatable, cost-adjusted short-horizon edges that survive leakage controls, multiple-testing controls, regime changes and execution friction.

## Scope
- Instrument: BTCUSDT perpetual futures on Binance Futures.
- Style: scalping.
- Initial horizons: 1, 2, 3 minutes; 5 minutes is the upper boundary.
- Sub-10-second research is deferred until actual latency is demonstrated adequate.
- Stage 1: historical trade/price data.
- Stage 2: forward L2 data collected from project start.
- Live trading: disabled until all gates pass.

## Status ladder
`HYPOTHESIS -> CANDIDATE -> PAPER-VALIDATED -> LIVE-CANDIDATE`

TBM is a labeling/evaluation framework, not itself a trading strategy. PT, SL and holding horizon must not be selected using future test outcomes.

## Validation rules
- Temporal walk-forward validation; no random train/test split.
- Purge and embargo are mandatory.
- Overlapping labels require concurrency/uniqueness handling.
- Model A vs Model B uses paired event differences.
- Block bootstrap tests calendar/regime dependence.
- FDR controls multiple hypothesis testing.
- Experiment family is assigned before results and is immutable.
- AI hypotheses are generated in frozen batches. Adaptive follow-up is a new batch with new lineage.

## Stage separation
Stage 1 can select candidates. Stage 2 is a separate forward L2 confirmation dataset. Stage 1 effect size is never the final live expectancy estimate.

## Required robustness gates
1. Data integrity
2. Effective sample size
3. OOS expectancy
4. Cost-adjusted EV
5. Confidence interval
6. Multiple-testing control
7. Regime stability
8. Period concentration

Thresholds are protocol parameters that must be locked before relevant candidate results are used for acceptance decisions.
