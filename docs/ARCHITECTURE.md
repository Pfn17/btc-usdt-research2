# BTCUSDT Research 2 — Architecture Contract

## Purpose
Research-first system for BTCUSDT perpetual futures on Binance Futures. The system discovers and validates short-horizon, cost-adjusted edges before any live-trading consideration.

## Non-negotiable boundaries
- Binance BTCUSDT perpetual is the execution-data authority.
- Historical full L2 is not assumed; L2 begins at project collection start.
- Raw L2 is immutable and archived outside Supabase.
- Supabase stores structured metadata, indexes, health, labels, features, experiments and results.
- Provider infrastructure is portable through adapters and environment configuration.
- Live trading is disabled until explicit research/execution gates pass.
- No API keys or secrets are committed to Git.

## Logical components
1. `collector`: Binance depth stream + snapshot acquisition.
2. `orderbook`: local book reconstruction and sequence-gap recovery.
3. `integrity`: gap/rebuild detection and contamination intervals.
4. `archive`: immutable raw event archive interface.
5. `metadata`: Supabase persistence for structured state.
6. `research`: events, TBM, MFE/MAE, uniqueness, walk-forward evaluation.
7. `execution`: spread, walk-the-book impact, fees, latency and implementation shortfall.
8. `experiments`: hypothesis lineage, frozen batches and research freeze.
9. `dashboard`: observability/research UI; never implicitly enables trading.

## Data flow
Binance Futures depth stream + REST snapshot -> local order book -> integrity validation -> immutable raw archive -> derived features -> research/evaluation -> experiment registry/results.

## Deployment abstraction
The collector must run locally and on Railway or Render without core-code changes. Dashboard/API may run on Vercel. Replit/Codespaces are development environments, not production dependencies.
