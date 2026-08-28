# M5 — Model & Research

Status: **IMPLEMENTED (research framework, not a performance claim)**

M5 implements the minimum research machinery required by Research Protocol v1. It does not declare a profitable strategy and does not enable live trading.

## Components

- **Hypothesis framework**: explicit experiment family and hypothesis IDs; research freeze fingerprints protocol parameters before acceptance decisions.
- **Labeling engine**: close-observation triple-barrier labels with explicit time barrier. Ambiguous future observations are not silently resolved.
- **Model training**: deterministic, dependency-light logistic baseline plus standardization. This is a baseline, not a final model.
- **OOS validation**: temporal walk-forward split generator with explicit purge and embargo parameters; random splits are not used.
- **Cost/slippage model**: explicit fee, half-spread, slippage and latency components with round-trip cost calculation.
- **Paired evaluation**: event-aligned Model A vs Model B differences.
- **Robustness**: block bootstrap, Benjamini-Hochberg FDR, and interval-overlap uniqueness weights.

## Protocol alignment

The implementation follows the project research protocol: temporal validation, purge/embargo, overlapping-label awareness, paired comparisons, block bootstrap, FDR, immutable experiment-family semantics, and frozen hypothesis batches. Stage 1 and forward L2 confirmation remain separate datasets.

## Important limitations

1. The labeler operates on supplied future observations; it does not fetch future data itself and therefore cannot by itself guarantee source-level leakage prevention. Dataset construction must enforce the event-time boundary.
2. Close-only observations cannot establish intrabar TP/SL ordering. The implementation does not invent that ordering.
3. The logistic model is a baseline implementation, not evidence of predictive edge.
4. Cost parameters must be frozen before evaluating the relevant candidate family.
5. Contaminated L2 intervals must be filtered by the upstream integrity/research dataset before labels/features are accepted.
6. A real backtest/execution simulator, experiment registry persistence, and Stage-2 forward L2 confirmation are still required before any live-candidate decision.

## Acceptance checklist

- [x] Hypothesis Framework
- [x] Labeling Engine
- [x] Model Training baseline
- [x] OOS Walk-forward utility
- [x] Purge + Embargo parameters
- [x] Cost / Slippage model
- [x] Paired event evaluation
- [x] Block Bootstrap
- [x] FDR control
- [x] Uniqueness weighting
- [x] Research tests
- [ ] Profitability claim
- [ ] Live trading
