# Executable PnL contract — v1.0

Status: FROZEN 2026-09-22

The purpose of this contract is to prevent a reported proxy return from being silently treated as executable trading PnL.

## Contract

1. **Decision time** — a signal may use only information available at or before its decision timestamp.
2. **Entry** — the fill price must be explicitly defined. For 1-minute OHLCV research, a preregistered next-bar/open rule may be used; an unstated close-to-close proxy is not executable PnL.
3. **Exit** — the exit timestamp and executable fill rule must be preregistered. If the required price path is unavailable, the observation is invalid rather than bridged.
4. **Fees** — baseline is 4 bps per side.
5. **Slippage** — baseline is 1 bps per side.
6. **Round-trip baseline** — 10 bps.
7. **Stress** — 12 bps round trip.
8. **Latency** — latency must shift the executable fill timestamp when modeled; a 0 ms assumption is valid only where explicitly preregistered.
9. **Funding** — funding cashflow is included whenever a position crosses a funding event.
10. **Overlap** — trades are non-overlapping unless a different rule is frozen before OOS.
11. **Missing data** — missing timestamps invalidate affected windows; no interpolation or silent bridging.
12. **Promotion** — positive net EV, CI95 entirely above zero, declared stress survival, and minimum independent-time coverage are required. Trading authorization remains OFF until separately approved.

## Required evidence

Every future promoted result must expose:

- signal timestamp;
- decision/availability timestamp;
- entry timestamp and price;
- exit timestamp and price;
- fee and slippage assumptions;
- latency assumption;
- funding cashflow when applicable;
- overlap rule;
- invalid/missing-window count;
- dataset cutoff and implementation identity.

A gross forward-return statistic that cannot satisfy these fields is research evidence, not executable PnL.
