# M8 Research Audit — 2026-09-01

## Purpose
Record the quantitative audit performed against the live Supabase dataset and keep the research conclusions reproducible.

## WFO correction
The production `research_wfo_signal_scan` SQL function was replaced in Supabase with a leakage-hardened implementation while preserving the existing RPC signature.

Important controls now enforced in the function:
- entry observations are frozen at `as_of_event_time_ms - horizon - 3s`;
- future labels must come from the same `session_id`;
- future matching is bounded to the requested horizon plus 3 seconds;
- purge is at least the label horizon;
- thresholds are estimated strictly before the test start minus effective purge;
- chronological folds remain 2–5;
- cost is `2*fee + spread + 2*slippage` in bps;
- live trading remains disabled.

The existing API endpoint continues to call the same function name, so no application-side migration is required for this correction.

## Frozen reproducibility check
Using cutoff `1788261186096`, horizon 60s, sample 50,000, purge 60s, embargo 60s, fee 4 bps/side, slippage 0, the corrected function reproduces the previously reported negative taker economics:
- fold 2: -6.3369 bps
- fold 3: -6.5765 bps
- fold 4: -7.2277 bps
- fold 5: -7.6011 bps

This confirms the cost gate is not being caused by the dashboard layer.

## Current live-cutoff result
At cutoff `1788267193358`, the same 4 bps/side taker model remains negative across all four OOS folds:
- fold 2: -7.4059 bps
- fold 3: -7.2994 bps
- fold 4: -6.5546 bps
- fold 5: -7.1968 bps

## Maker sensitivity
A new read-only RPC `research_maker_wfo_scan` was added to evaluate passive-execution economics under explicit fill-probability scenarios (25%, 50%, 75%, 100%) and configurable maker fee.

At maker fee 2 bps/side, the frozen test produced negative full-fill EV in every fold. At zero maker fee, full-fill EV remained positive in every fold, but the weakest fold was only about +0.42 bps. Therefore the present feature effect is too small to support a base-tier Binance maker strategy without a materially better execution edge.

This is a sensitivity model, not a claim of actual fill probability. The collected dataset does not yet contain order-level queue position or user-order fill events.

## Feature-family screen
A read-only `research_wfo_feature_scan` RPC was added for directional screening of imbalance, book pressure, order flow, and microprice deviation under the same temporal/cost framework.

At 4 bps/side all screened directional features were negative OOS. At zero fee, microprice deviation, imbalance, and book pressure showed small positive OOS effects, while order flow was approximately flat.

These are screening results, not live-edge approvals. Multiple-testing/FDR, block bootstrap, regime stability and executable fill modeling remain required before any paper signal can be promoted.

## Runtime
The live feature store remains healthy. Recent snapshots show feature computation around 15–18 ms and feature age below 1 second, so the earlier ~25.5 second dashboard value was instrumentation/measurement behavior rather than current feature computation time.
