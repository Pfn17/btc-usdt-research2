# BTCUSDT Edge Research — Experiment Ledger

Updated: 2026-09-08

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

## Production archive synchronization — 2026-09-09

The production Supabase registry contains `fam-swing-v1` and a frozen `H-SW1` row. Two separate research RPC lineages are now live and versioned:

- `research_sw1_scan_frozen(text,numeric,numeric,integer)` — **H-SW1-CLAUDE**, the original reference method.
- `research_sw1_manus_scan_frozen(bigint,numeric,numeric,integer)` — **H-SW1-MANUS**, an independent method with a different candidate grid, funding agreement rule, and period grouping.

The Manus function was applied by migration `20260908025302` and is represented in Git by commit `1153323`. The two methods must not be merged, silently substituted, or reported as mutual confirmation. The live read-only verification recorded in `docs/HSW1_LIVE_VERIFICATION_2026-09-09.md` found both methods **INCONCLUSIVE / NOT PROMOTED** because their overall CI95 intervals cross zero. Neither method is a trading signal.

The portfolio dashboard is a **Research Archive** with three local presentation modes: Terminal, Apple, and Story / Visual. The modes change presentation only; they use the same backend-derived data and do not enable execution. The dashboard commit is `689dcd4`. The archive must not present `LONG`, collector health, or any other observed state as profitability, a validated edge, or trading approval. H-FB1 remains **KILL**, the funding family remains **CLOSED**, H-SW1 remains **INCONCLUSIVE**, and execution remains **OFF**.

The implementation and live verification are now synchronized across Git, Supabase, and this ledger. Any future method with materially different logic must receive a new hypothesis identity and independent frozen specification rather than reusing H-SW1.

## Hard Stop

If the current candidate fails its frozen OOS gate, kill it. Do not optimize around the result.


## H-FB3 five-gap closure — 2026-09-10

The independent audit of H-FB3 identified two presentation defects and three provenance/governance gaps. The persisted outcome itself is unchanged: `N=2,984`, net EV `-10.118565 bps`, CI95 `[-10.793438, -9.443693] bps`, stress net EV `-12.118565 bps`, status `KILLED`, and trading disabled.

The dashboard now reads the stress value from `evidence.stress_net_bps` and includes H-FB3 as a fourth row in the EV/CI comparison chart. The discarded earlier `N=4,692` run is now retained as an append-only audit trace with its wrong OOS timestamp-window reason; it is not evidence and does not replace the official result. The exact frozen OOS window is reconciled to commit `fd712a286f4ef79476da11dcf985a8650c7008eb`: `2026-08-03T00:00:00Z` through `2026-09-09T23:59:59.999Z`, with query cutoff `2026-09-10T10:18:00Z`.

For future confirmatory families, the project default is now prospective Benjamini–Hochberg FDR at `q=0.05` across a predeclared hypothesis universe, declared before outcomes are opened. Exploratory scans cannot be promoted as confirmatory findings. Each hypothesis must still pass its own frozen economic, confidence, temporal, and cost gates. No retroactive FDR adjustment is applied to H-FB3; it remains an unadjusted pre-registered KILL. No H-FB4 or later confirmatory outcome may be opened without a family registry and FDR declaration. Full evidence is recorded in `docs/H-FB3_AUDIT_ADDENDUM_2026-09-10.md` and `public.agent_coordination_log`.
