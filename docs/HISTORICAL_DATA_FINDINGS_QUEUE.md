# Historical Data Findings Queue

Updated: 2026-09-22

Purpose: preserve external research/data sources for later forensic review without importing their strategies into the active hypothesis program.

## Status

These sources are **FINDINGS ONLY**. No fork, fine-tuning, strategy adoption, or OOS experiment is authorized by this record.

## Findings

### Gotodataru/binance-futures-backtest
Source: https://github.com/Gotodataru/binance-futures-backtest

Observed from public repository material:
- Binance USDT-M perpetual research/backtest framework.
- Documents 1m OHLCV, funding, OI and long/short-ratio style market metrics over a multi-year period.
- Includes funding mean reversion, taker-buy pressure momentum, and OI + price divergence strategy families.
- Documents walk-forward validation and next-bar execution assumptions.

Research value:
- Potential source for historical OI/market-metric data or reproducible acquisition paths.
- Potential methodology reference only until independently reconstructed.

Caution:
- Publicly displayed positive examples are not treated as proof of a profitable BTCUSDT edge.
- Raw-data redistribution rights and actual dataset availability must be verified before copying anything.

### OctopusTakopi/crypto-trend-following
Source: https://github.com/OctopusTakopi/crypto-trend-following

Observed:
- CTA/trend-following research on Binance perpetuals.
- Explicit source/provenance discussion and frozen-rule methodology.
- Uses Binance Vision historical data.

Research value:
- Data acquisition/provenance pattern.
- External methodology reference.

No strategy adoption authorized.

### Pavdot/btcusdt-strategy-optimizer
Source: https://github.com/Pavdot/btcusdt-strategy-optimizer

Observed:
- BTCUSDT-specific backtesting/optimization project.
- Walk-forward, Monte Carlo and reproducibility-oriented workflow.
- Raw Binance data is expected locally rather than committed to Git.

Research value:
- Validation/research-engineering pattern.
- Possible historical-data acquisition reference.

No strategy adoption authorized.

### Freqtrade/freqtrade-strategies
Source: https://github.com/freqtrade/freqtrade-strategies

Observed:
- Large collection of community strategies.
- Useful as a broad idea/research corpus.

Research value:
- Idea discovery only.
- High multiple-testing/data-mining risk means no community backtest result is treated as evidence for HyperHan.

No blind optimization or strategy import authorized.

### makson0krut/btc-strategy-lab
Source: https://github.com/makson0krut/btc-strategy-lab

Observed:
- BTC/USDT perpetual strategy research lab.
- Public material documents rejection of tested trend-pullback and mean-reversion approaches after costs.

Research value:
- Negative-control/base-rate reference.
- Methodology and failure evidence.

No strategy adoption authorized.

## Data architecture decision

HyperHan should avoid turning Supabase into a raw historical-data warehouse.

Target architecture:

external source/archive -> immutable archive -> research compute -> compact evidence/results -> Supabase

Supabase should hold:
- dataset registry and provenance metadata;
- experiment/hypothesis state;
- compact research results;
- audit/replay metadata;
- bounded dashboard state.

Raw candles, trades, order books, OI series, liquidation streams and other large historical payloads should live outside Supabase when practical.

The dataset registry records where a dataset lives, its period/schema, checksum, provenance and redistribution status. It does not contain the raw dataset.

## Guardrail

Do not copy or redistribute external raw data until source availability, license/terms, and redistribution status have been verified. Prefer reproducible acquisition from an authoritative source when possible.

Next permitted activity: forensic data-source audit only.
