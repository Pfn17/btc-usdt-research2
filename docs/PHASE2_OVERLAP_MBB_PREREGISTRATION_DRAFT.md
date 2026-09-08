# Phase 2 — Overlap MBB Preregistration Draft

**Status:** DRAFT — **NOT RUN**  
**Lineage:** new method; does not modify or replace either legacy H-SW1 function.  
**Trading:** disabled.  
**Dashboard:** no new signal panel until validation passes.

## Why execution is paused

The project plan requires the following choices to be frozen before any result is viewed: entry cadence, label horizon, candidate timestamp rule, momentum definition, funding agreement, funding cashflow interval, cost model, discovery/OOS cutoff, block unit, block length rule, bootstrap count, seed, and promotion/kill gates. The repository contains the warning and the legacy 24-hour/day-cadence implementation, but it does not contain an owner-approved, complete Phase 2 specification. Running now would require silently selecting material parameters.

## Proposed choices for owner approval

| Parameter | Proposed value | Owner decision required |
|---|---|---|
| Entry cadence | Every 1 hour at exact UTC `HH:00:00.000` | Approve or change |
| Horizon | Exactly 24 hours | Approve or change |
| Candidate start | First available BTCUSDT 1m candle at or after the UTC hour | Approve or change |
| Momentum | Signed return from entry time minus 24 hours to entry time; direction follows sign | Approve or change |
| Funding agreement | Three most recent completed funding events before entry; unanimous positive/negative sign | Approve or change |
| Funding cashflow | Sum funding events strictly after entry and through exit, inclusive at exit | Approve or change |
| Direction gate | Require momentum sign and funding agreement sign to agree; otherwise no observation | Approve or change |
| Cost model | 4 bps fee per side plus 1 bps slippage per side; 10 bps round-trip total | Approve or change |
| Discovery/OOS split | First 70% of chronological eligible observations for implementation checks; final 30% untouched OOS | Approve or change |
| Block unit | Fixed 24-hour time blocks to preserve the 24-hour label dependence | Approve or change |
| Block sensitivity | Report 12h, 24h, and 48h blocks; do not select the best one | Approve or change |
| Bootstrap | Moving-block bootstrap of net returns with 10,000 replications | Approve or change |
| Random seed | `20260908` | Approve or change |
| Minimum OOS observations | 30 eligible OOS observations | Approve or change |
| Promotion gate | Net OOS EV > 0; robust CI lower bound > 0 for every predeclared block sensitivity; positive result in a predeclared majority of OOS calendar blocks; survives cost stress | Approve or change |
| Kill gate | Any mandatory promotion condition fails, data gap/leakage is found, or result depends on one isolated block | Approve or change |
| Public disclosure | Aggregate result only; method and private edge details remain hidden; trading remains disabled | Approve or change |

## Required implementation boundary

SQL may emit a deterministic per-observation dataset only. Bootstrap inference must run in a versioned, local Python script outside production SQL. The output must include entry time, exit time, entry/exit prices, momentum, funding state, raw return, funding cashflow, net return, and label interval. The script must record the Git commit, specification hash, cutoff, row counts, seed, block sensitivity, and output checksum.

## No execution before approval

This document is intentionally a draft. No Phase 2 scan, migration, RPC, backfill, dashboard panel, or production endpoint is authorized by this draft alone. The owner must approve the complete parameter table or provide replacements. After approval, the parameter table will be copied to a versioned preregistration, hashed, committed, and logged before any result is computed.
