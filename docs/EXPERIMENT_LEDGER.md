# BTCUSDT Edge Research — Experiment Ledger

Updated: 2026-09-04

## Objective

Primary objective is **not** to build a bot until it is profitable.

> Find one conditional trading setup with positive **net EV out-of-sample (OOS)** that is reproducible.

If a hypothesis fails, kill it. Do not add indicators or infrastructure to rescue it.

## Operating Contract

### Stage 1 — Explore
- Use only existing tables/data.
- Cheap SQL/RPC analysis.
- No new Railway services, dashboard work, or production infrastructure.
- A hypothesis must be written and frozen before querying results.

### Stage 2 — Validate
- Use data not used for discovery.
- Include fees, slippage, and latency assumptions.
- A candidate must survive OOS.
- Net EV <= 0 OR CI95% crossing zero => kill.
- Do not retune after seeing validation results.

### Stage 3 — Paper
- Only after Stage 2 passes.
- Then serious real-time collector/dashboard/persistent signal logging is justified.
- Live order execution remains OFF until independently validated.

## H-FB1 — KILL

Family: Funding / follow-sign.

Result already established:
- Gross EV: approximately +5 bps
- Net EV after 10 bps RT cost: approximately -5 bps
- Win rate: 44.44%
- Net CI95%: approximately [-12.74, +2.75] bps

Decision: **KILL**.

Do not retune H-FB1 on the same data.

## H-FB2 — KILL

Hypothesis: extreme funding crowding is faded until the next actual funding print.

Frozen rules:
- Train = first 60 days of funding events, ordered by timestamp.
- OOS = remaining ~30 days.
- Q10/Q90 calculated once from train only.
- Frozen Q10 = -0.000082.
- Frozen Q90 = +0.000095.
- Funding <= Q10 -> LONG.
- Funding >= Q90 -> SHORT.
- Exit = next actual funding print.
- Entry = markPrice at funding event (for the completed external test).
- Cost = 4 bps + 1 bps per side = 10 bps round trip.
- Funding cashflow at next print included.
- No changing Q, direction, hold, regime, RSI, EMA, or other filters.

Reported results:
- Train: N=36, gross +2.0 bps, net -8.0 bps, win 44%.
- OOS: N=29, gross -16.1 bps, net -26.1 bps, win 45%.
- OOS net CI95%: approximately [-72, +19] bps.

Decision: **KILL**.

The OOS being all short is an observed regime characteristic, not a reason to change the rule.

## Funding Family Status

H-FB1 = KILL.
H-FB2 = KILL.

**2/2 failed -> funding family CLOSED temporarily.**

Do not run Q80/Q20, alternative holding periods, sign-follow variants, regime filters, or combined indicators as follow-ups to this family.

## Next Allowed Work — Option A

Next work may be exactly **one OHLCV/HTF hypothesis (H-FB3)**.

Before querying:
1. Write the mechanism/story.
2. Freeze every material knob: feature definition, timeframe, entry, exit/horizon, train/OOS split, costs, latency, and pass/kill gate.
3. Use existing OHLCV data only.
4. Do not inspect outcomes before the specification is frozen.
5. Query once for discovery, then validate on untouched OOS.
6. No infrastructure build unless the candidate passes Stage 2.

The exact H-FB3 specification is **not yet chosen** and must be frozen before testing.

## Infrastructure Debt

Existing Stage-3 infrastructure was built before Stage-2 proof. Treat it as debt, not evidence of edge.

Existing signal/audit logs should be preserved and never reset merely to make a new experiment cleaner.

## Hard Stop

If the current candidate fails its frozen OOS gate, kill it. Do not optimize around the result.
