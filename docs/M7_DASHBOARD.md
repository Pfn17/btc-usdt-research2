# M7 — Dashboard

Status: **IMPLEMENTED (read-only observability/research surface)**

M7 adds a lightweight dashboard served by the existing FastAPI application. It is intentionally read-only and does not enable trading or mutate research configuration.

## Implemented

- Market overview from the latest validated feature snapshot
- Feature viewer for spread, microprice, imbalance, depth, order flow, volatility and book pressure
- Data freshness / integrity state from the existing `/health` and feature endpoints
- Collector session/runtime state
- Feature compute latency display
- Automatic refresh every 5 seconds
- Explicit unavailable states for order-book depth, signal and research/backtest data when the backend does not yet expose those datasets

## Data boundary

The dashboard consumes the existing read-only FastAPI endpoints:

- `/health`
- `/api/v1/features/latest`
- `/api/v1/collector/health`
- `/api/v1/session/current`
- `/ws/features` (backend capability retained for future streaming UI)

It does not write to Supabase, change experiment parameters, place orders, or introduce exchange credentials.

## Important non-fabrication rule

The dashboard must not display a synthetic order book, signal, backtest result, confidence score, expected move, or profitability claim when the corresponding backend data is unavailable. M7 therefore shows explicit unavailable states for those panels until the required read APIs exist.

## Acceptance checklist

- [x] Market Overview
- [ ] Order Book Depth — requires a read-only order-book endpoint
- [x] Integrity Monitor
- [x] Latency Monitor
- [x] Feature Viewer
- [ ] Signal Panel — requires a validated signal endpoint
- [ ] Research / Backtest — requires research result read endpoints
- [x] Read-only boundary
- [x] Responsive UI

## Next integration targets

1. Add a read-only current-order-book endpoint backed by the validated local book.
2. Expose research registry/result summaries without exposing write operations.
3. Add signal display only after a validated signal contract exists.
4. Replace polling with the existing WebSocket stream for the live feature cards where useful.
