# H-SW1 Live Verification — 2026-09-09

**Verifier:** Manus 1 via Supabase MCP connector  
**Project:** `btc-usdt-research2` / ref `xaqsntunrqvqpzlbeutt`  
**Verification type:** read-only live database verification  
**Cutoff:** latest `ohlcv_1m.open_time_ms = 1788940200000` at query time  
**Database status:** `ACTIVE_HEALTHY`

## Function identity

The live database contains exactly two distinct H-SW1-related functions:

| Method | Signature | RPC |
|---|---|---|
| H-SW1-CLAUDE | `research_sw1_scan_frozen(text,numeric,numeric,integer)` | `research_sw1_scan_frozen` |
| H-SW1-MANUS | `research_sw1_manus_scan_frozen(bigint,numeric,numeric,integer)` | `research_sw1_manus_scan_frozen` |

The original Claude function uses `p_as_of_ms text` and internally parses the epoch value. The Manus function uses `p_as_of_ms bigint`. They are not overloaded under the same name and are not treated as interchangeable.

## Live call parameters

Both methods were called with the frozen cost and lookback parameters:

| Parameter | Value |
|---|---:|
| Fee per side | 4 bps |
| Slippage per side | 1 bps |
| Funding lookback | 3 events |
| Horizon | 24 hours |
| As-of cutoff | `1788940200000` |

The Claude RPC was called with `NULL::text`, which invokes its internal latest-OHLCV cutoff. The Manus RPC was called explicitly with `(SELECT max(open_time_ms) FROM ohlcv_1m WHERE symbol='BTCUSDT')` because the Manus function has no default cutoff. Both resolved to the same latest cutoff.

## Live results

### H-SW1-CLAUDE

| Bucket | N | Gross EV (bps) | Net EV (bps) | Win rate | Net CI95 (bps) |
|---|---:|---:|---:|---:|---:|
| Overall | 38 | 10.4815 | 0.4815 | 52.63% | -48.8390 to 49.8020 |
| Quarter 1 | 10 | -29.5955 | -39.5955 | 40.00% | -145.1383 to 65.9472 |
| Quarter 2 | 10 | 69.1982 | 59.1982 | 60.00% | -22.1389 to 140.5352 |
| Quarter 3 | 9 | 11.2683 | 1.2683 | 66.67% | -100.8539 to 103.3906 |
| Quarter 4 | 9 | -11.0159 | -21.0159 | 44.44% | -130.3783 to 88.3466 |

### H-SW1-MANUS

| Bucket | N | Gross EV (bps) | Net EV (bps) | Win rate | Net CI95 (bps) |
|---|---:|---:|---:|---:|---:|
| Overall | 44 | 32.3353 | 22.3353 | 43.18% | -43.2269 to 87.8975 |
| Calendar Q2 2026 | 6 | -48.2010 | -58.2010 | 33.33% | -202.7810 to 86.3789 |
| Calendar Q3 2026 | 38 | 45.0516 | 44.44% | 44.74% | -37.1638 to 107.2669 |

## Decision

Both live methods are **INCONCLUSIVE / NOT PROMOTED**. Neither is a validated edge because each overall confidence interval crosses zero. The Manus point estimate is not comparable to the Claude point estimate as a confirmation because the candidate grid, funding agreement rule, and period bucketing differ.

The dashboard must preserve both method identities and display unavailable states when a live RPC cannot be reached. Neither method enables paper trading or live execution.

## Important evidence boundary

The live function inspection and RPC outputs verify availability, signatures, cutoff, and current returned rows. This does not independently prove the historical `research_results` record or the external report's original cutoff. The official H-SW1 registry row exists with `horizon_seconds=86400`, but the `research_results` table schema has no direct `hypothesis_id` column; any lineage join requires the appropriate model/split registry mapping before claiming an exact match.

No DDL or data mutation was performed during this verification.
