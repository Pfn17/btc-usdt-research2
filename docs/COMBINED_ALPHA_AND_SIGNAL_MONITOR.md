# Combined Alpha + Signal Monitoring

## Primary objective

Find **one repeatable positive NET-EV mechanism** by combining two paradigms available on Binance Futures:

1. L2 microstructure: imbalance / microprice / order-flow / spread / volatility.
2. OHLCV: 1m candle return and later volume-derived regimes.

A mechanism is not promotable from exploratory EV. It must survive frozen chronological OOS, purge/embargo, overlap-aware uncertainty, realistic costs, and forward paper validation.

## Current evidence (2026-09-02)

- `feature_snapshots`: ~1.35M BTCUSDT rows are available for L2 research.
- Baseline imbalance WFO at fee=0 is not robust: fold 2 +0.606 bps, fold 3 -0.692, fold 4 +0.513, fold 5 -0.510.
- Baseline imbalance WFO at 4 bps/side is decisively negative across all folds.
- Existing preregistered conditional L2 hypotheses are also not robust. At fee=0, both `imbalance_microprice_lowspread` and `imbalance_orderflow_lowspread` have negative folds 3 and 5.
- `ohlcv_1m` currently has only ~137 live rows; 90-day historical backfill is blocked by the current Binance 418/IP-ban incident. Therefore combined L2+OHLCV discovery is **blocked on data volume**, not on research design.

## Frozen combined hypothesis

**L2 imbalance + closed 1m momentum agreement**.

At each L2 feature timestamp:

- Use only the most recently **fully closed** BTCUSDT 1m candle.
- Compute candle return `(close-open)/open`.
- Compute imbalance thresholds from training data only: Q20/Q80.
- LONG only when imbalance >= train Q80 AND closed 1m return > 0.
- SHORT only when imbalance <= train Q20 AND closed 1m return < 0.
- Horizon: 60 seconds.
- Purge: >= 60 seconds.
- Embargo: >= 60 seconds.
- Cost: evaluate fee=0 first for information content, then realistic fee + slippage.
- No threshold sweep, no ML, no volume threshold sweep, no post-hoc direction selection.

The SQL function `research_combined_alpha_scan_frozen` is stored in migration `20260902_combined_alpha_and_signal_audit.sql`. It is intentionally not applied while another agent has an active infrastructure task on the Supabase resource.

## Kill / promotion rules

Kill the combined hypothesis if the frozen OOS result does not materially exceed the existing ~1 bps microstructure family and fails stability across folds. A candidate must not become a paper signal merely because one fold is green.

Before any live order:

- every OOS fold positive;
- corrected uncertainty lower bound > 0;
- net EV positive after realistic execution cost;
- signal frequency sufficient for meaningful forward testing;
- forward paper test confirms the same direction/EV;
- live execution remains OFF until independently verified.

## Signal monitoring requirement

The dashboard must not be the only source of truth. A signal evaluation must be persisted server-side so a human can later answer:

- Did a candidate signal occur?
- When did it start/end?
- LONG or SHORT?
- Why was it accepted/rejected?
- What was the data-quality and cost gate state?
- How many candidate events happened while nobody was watching?

Migration adds `signal_audit_events` with an immutable event timestamp, status, direction, rationale, gate JSON and feature JSON. The runtime writer/alert loop must record state transitions and candidate events; the dashboard can then show `MISSED/UNSEEN` counts based on the last acknowledged event.

## Do not repeat

- Do not resume threshold hunting inside the rejected L2-only conditional batch.
- Do not call exploratory scanner green rows a validated edge.
- Do not start ML, full HFT simulation, walk-the-book simulation, or raw-depth long-term archival for this objective.
- Do not enable live trading from the current signal endpoint.
