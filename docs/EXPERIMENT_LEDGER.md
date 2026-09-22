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

## Next Allowed Work — H-MR1

The next OHLCV hypothesis is **H-MR1 — Intraday Extreme-Candle Mean Reversion**. It is a new reversal mechanism, not a continuation or funding-family follow-up.

The specification is frozen in `docs/H-MR1_PREREGISTRATION.md` and implemented as a separate read-only RPC:

`research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric)`

Frozen controls include the train-only 95th percentile of absolute 15-minute returns, opposite-direction entry, one-hour exit, chronological non-overlap, explicit OOS cutoff, 10 bps baseline cost, 12 bps stress cost, weekly/direction breakdowns, and predeclared promotion/kill gates. The manual API route is `/api/v1/research/hmr1` and is not wired into the dashboard.

Current status: **FROZEN / IMPLEMENTED / UNRUN**. No H-MR1 outcome has been queried by this implementation. An independent verifier must inspect the migration and API before the first scan. Any result must be recorded as a new hypothesis row for project-wide multiple-testing accounting.

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


## H-VOL1 readiness implementation — 2026-09-12

H-VOL1 is registered as family `fam-vol-v1`, protocol `v1-fdr-q005`, with status `FROZEN_IMPLEMENTED_UNRUN`. The frozen mechanism is a strict 120-minute breakout confirmed by train-only taker-buy-ratio P90/P10, exact `t+1` entry, exact 120-minute exit, greedy chronological non-overlap, 10 bps baseline cost, and 12 bps stress cost. The exact OOS boundary is **not yet frozen**.

The owner-facing dashboard now exposes backend-derived H-VOL1 readiness only. It does not poll the outcome route, choose a cutoff, display profitability, or enable execution. Supabase readiness at `as_of_ms=1789064160000` reports `141,772` candles, `84` missing minutes versus `141,856` expected, `141,065` complete range windows, `141,772` valid taker ratios, no training/OOS split because no boundary was supplied, `outcome_run=false`, and `authorization=NOT GRANTED`. This is data-readiness evidence, not an outcome.

The live Supabase registry already contained H-VOL1 objects under migrations `20260912075810`, `20260912075927`, and `20260912080008`, while those historical migration files were absent from GitHub `main`. A source-reconciliation migration and handoff were added rather than creating a parallel hypothesis or silently replacing the live lineage. No H-VOL1 profitability/OOS scan was run. Independent audit remains required before any cutoff is frozen or outcome is queried. Full details: `docs/H-VOL1_PREREGISTRATION.md` and `docs/AGENT_HANDOFF_2026-09-12_HVOL1.md`.


## Stage-2 closure — 2026-09-20

### H-MR1 — KILL

Frozen OOS evaluation was executed with the owner-authorized boundary `2026-07-27T00:00:00Z` through the latest complete stored candle cutoff `2026-09-09T10:16:00Z`.

- OOS samples: 190
- Mean gross: +6.97 bps
- Net EV: **-3.03 bps**
- Stress net EV: **-5.03 bps**
- Net CI95: **[-12.02, +5.96] bps**
- Stress CI95: **[-14.02, +3.96] bps**
- Positive weeks: 3 / 7

Decision: **KILL** under the project gate because net EV is non-positive and the CI95 crosses zero. The result is recorded in `research_results`; trading remains disabled.

Data note: the dataset still contains 84 missing one-minute timestamps in the wider coverage range. The frozen scan uses exact timestamp joins and therefore does not fabricate or bridge missing candles. The missing-minute fact remains part of the audit record.

### H-VOL1 — KILL

The frozen breakout/taker-flow scan was executed against the same owner-authorized OOS boundary.

- OOS samples: 306
- Mean gross: +1.48 bps
- Net EV: **-8.52 bps**
- Stress net EV: **-10.52 bps**
- Net CI95: **[-14.90, -2.15] bps**
- Stress CI95: **[-16.90, -4.15] bps**
- Positive weeks: 1 / 7
- Max positive-week contribution share: 43.17%

Decision: **KILL**. Both economics and confidence are negative. No threshold retuning is permitted on this OOS.

### H-SW1 — CLOSED / NO PARAMETER EDGE

A closure robustness check was run for funding lookback values 2–5. The observed OOS result did not change: 17 signals, net EV **-19.43 bps**, CI95 **[-94.02, +55.15] bps** for the tested lookback values.

This does **not** constitute a new confirmatory hypothesis or a license for post-hoc optimization. It shows that changing the existing lookback parameter did not expose a useful lever in this sample.

Decision: **CLOSE H-SW1 for this dataset.** A materially different mechanism must receive a new hypothesis identity, preregistration, and independent OOS boundary. Do not continue tuning H-SW1 against the same OOS sample.


## Research system review — 2026-09-21

The project is pausing expansion of the hypothesis registry after repeated candidates failed to produce a validated, cost-adjusted trading edge. This is **not** a claim that the market has no edge. It is a checkpoint on whether the research system itself is capable of discovering an executable edge reliably.

The review scope is project-wide and must cover:

- **Data layer:** historical coverage, timestamp continuity, sampling frequency, missing data, extraction boundaries, and whether the collected fields are sufficient for the hypotheses being asked.
- **Feature layer:** timestamp alignment, leakage, availability at decision time, window construction, sparse snapshots, and feature correctness.
- **Hypothesis layer:** mechanism quality, testability, parameter freezing, entry/exit derivation, and whether rules are being selected before outcomes rather than after them.
- **Economics / execution model:** actual entry and exit price definitions, fees, slippage, latency, funding, overlap handling, and whether reported EV represents executable PnL.
- **OOS / statistics:** independent boundaries, regime coverage, sample dependence, contamination, extraction errors, and whether OOS is genuinely independent and sufficiently representative.
- **Agent workflow:** writer/verifier separation, reproducibility, evidence quality, coordination discipline, and whether agent activity is producing research value rather than documentation volume.

### Current decision

**PAUSE NEW HYPOTHESES.** Do not respond to the lack of profitability by simply adding another candidate. First verify that the research engine, data model, hypothesis construction, execution model, and validation pipeline are sound.

Existing experiment outcomes remain append-only evidence. No killed or inconclusive hypothesis may be rewritten or retuned merely to improve its result. Trading remains **OFF**.

The next permitted research milestone is a **project-level forensic review** followed by an owner-reviewed decision on whether the existing research architecture is fit for another hypothesis cycle.


## Research validation harness — 2026-09-22

A synthetic validation harness was executed before allowing another hypothesis cycle. The purpose is to test the decision path itself, not to manufacture a market result.

Run: `HARNESS-2026-09-22`

| Scenario | Expected | Observed | Harness |
|---|---|---|---|
| Known positive synthetic edge | PASS | PASS | PASS |
| Synthetic edge below declared cost | KILL | KILL | PASS |
| Synthetic look-ahead / leakage | REJECT | REJECT | PASS |
| Train-only synthetic edge that fails OOS | KILL | KILL | PASS |

The four scenarios all matched their expected decisions. The known-positive scenario used net EV +18 bps with CI95 [-2, +38] bps; this confirms the path can recognize a positive net-EV case, while the separate promotion gate still correctly requires CI95 to clear zero before a real candidate is promoted.

The harness is validation evidence only. It is not evidence of a BTCUSDT trading edge and does not reopen hypothesis expansion. Trading remains **OFF** and the project-level forensic review remains the next milestone.


## Project forensic review — 2026-09-22

The project-level forensic review was executed before allowing another hypothesis cycle. Full report: `docs/PROJECT_FORENSIC_REVIEW_2026-09-22.md`.

### Findings

- **Data:** 141,772 OHLCV 1m rows; 84 missing minutes remain part of the audit record. Funding basis has 10,510 snapshots, with only about 3 active OOS days in the recent H-BASIS1 mechanism scan. `feature_snapshots` currently has 0 rows.
- **Features:** the synthetic leakage harness passes, but production research RPCs still require function-level independent replay before any future promotion.
- **Hypothesis lineage:** the live migration history contains repeated repair/replacement/fast-path migrations. Multiple H-MR1/H-VOL1 implementations exist, and H-SW1 has two signatures. This is a reproducibility risk even when the final persisted result is correct.
- **Economics:** the 10 bps baseline and 12 bps stress model are consistently declared, but executable-PnL semantics must become a project-wide invariant covering exact signal availability, fill price, latency, funding cashflow, and overlap.
- **OOS/statistics:** no validated net-positive edge has been produced. Several results are economically negative; others are underpowered because independent time/regime coverage is short.
- **Agent workflow:** the coordination log contains stale proposed/in-progress states. Prior independent audits found real implementation/provenance mismatches, confirming that executor/verifier separation must be enforced rather than merely documented.

### Decision

**PAUSE NEW HYPOTHESES.**

The research engine is not proven broken, but the project is not yet clean enough to justify another hypothesis cycle. The next gate is to repair provenance and verification hygiene:

1. canonical implementation per historical result;
2. lock/supersede stale coordination tasks;
3. result-lineage manifest;
4. independent replay of representative killed and inconclusive results;
5. explicit executable-PnL contract;
6. minimum independent-time requirement for promotion;
7. retain the synthetic harness as a regression test.

Historical evidence remains append-only. No failed result is retuned. Trading remains **OFF**.


## Forensic gate execution — 2026-09-22

The forensic gate was executed in four parts.

### 1. Canonical lineage

A result-lineage manifest is now recorded in `docs/RESULT_LINEAGE_MANIFEST_2026-09-22.md`.

- H-MR1 canonical implementation: `research_hmr1_scan_frozen_v2(bigint,bigint,numeric,numeric,numeric)`.
- H-MR1 replay matched the stored result exactly: N=190, net EV -3.0303795 bps, stress -5.0303795 bps, with matching confidence bounds.
- H-BASIS1 cannot currently be reproduced from the live canonical RPC. The historical result was N=156, while the current RPC replay returns N=7,412 for agreement=0 and N=2,862 for agreement=1.
- H-BASIS1 is therefore marked **MISMATCH / provenance blocked** until the exact historical implementation is recovered.

This is a reproducibility finding, not a claim that the historical result was fabricated.

### 2. Independent replay

The representative killed result H-MR1 passed canonical replay. The representative inconclusive result H-BASIS1 failed the reproducibility check because the current implementation does not generate the historical result.

No result was rewritten and no parameter was changed.

### 3. Executable-PnL contract

`docs/EXECUTABLE_PNL_CONTRACT.md` freezes v1.0.

The contract requires explicit decision-time availability, executable entry/exit rules, 4 bps fee + 1 bps slippage per side baseline, 12 bps stress, latency treatment, funding cashflow where applicable, overlap rules, missing-data invalidation, and minimum independent-time coverage for promotion.

A gross forward-return proxy is not to be represented as executable PnL unless these fields are satisfied.

### 4. Regression gate

Run: `FORENSIC-GATE-2026-09-22`.

The four synthetic harness scenarios all passed. H-MR1 canonical replay passed. H-BASIS1 canonical replay failed.

Therefore the overall regression gate is **BLOCKED**, not passed.

### Agent-state hygiene

All stale `proposed` / `in_progress` coordination entries were locked as historical trace on 2026-09-22. No stale task is allowed to silently reopen hypothesis work.

### Current decision

**PAUSE NEW HYPOTHESES remains in force.**

The remaining blocker is exact historical provenance recovery for H-BASIS1. The next action is not a new edge search and not retuning; it is to recover and identify the implementation that generated the N=156 result, then rerun the regression gate.

Trading remains **OFF**.


## Forensic gate R2 — 2026-09-22

After the H-BASIS1 provenance recovery, the existing forensic gate was replayed as `FORENSIC-GATE-2026-09-22-R2`. All six required checks passed: the four synthetic decision-path scenarios, canonical H-MR1 replay, and exact historical H-BASIS1 replay. The H-BASIS1 replay matched N=156 and the stored primary 15-minute metrics using the historical implementation commit and frozen dataset hash. The current funding-basis RPC was not substituted for the recovered historical implementation.

**Overall R2: PASS as a regression/provenance gate only.** This does not promote any strategy, does not change any historical economic outcome, and does not reopen hypothesis generation. H-BASIS1 remains **INCONCLUSIVE / UNDERPOWERED** because its net proxy EV is negative and its OOS coverage is only three active UTC days. Research remains paused, historical evidence remains append-only, retuning is forbidden, and trading remains **OFF**.

The dashboard now publishes the historical result archive, the recovered H-BASIS1 provenance detail, the project state `PAUSED — NO NEW HYPOTHESES`, the R2 gate state, and the `Founder & Principal Researcher` authority label as read-only research context.


## Gate 0 — Executable PnL permission gate — 2026-09-22

Gate 0 was upgraded from a cost document into a permission contract. Contract v1.1 defines three economic evidence classes: EXECUTABLE_PNL, FORWARD_RETURN_PROXY, and UNVERIFIABLE. Only the first class may support a profit or promotion claim.

The contract now requires decision-time availability, signal/fill/evaluation timestamps, explicit entry and exit prices, applied latency, fees, slippage, funding cashflow when applicable, overlap state, invalid reason, dataset cutoff, and implementation identity. Missing evidence cannot silently become an executable trade.

The deterministic economics harness run is GATE0-2026-09-22: 8/8 synthetic checks passed, covering LONG/SHORT formulas, 10 bps cost, latency fill shift, missing exit invalidation, overlap suppression, funding cashflow, and rejection of post-decision information. Supabase regression registry records the run and an overall Gate 0 PASS.

Historical classification is intentionally conservative. H-MR1 and H-BASIS1 remain historical research evidence but are FORWARD_RETURN_PROXY under the v1.1 executable invariant. H-VOL1 remains unrun and unauthorized. H-FB3, H-FB2, H-FB1/Funding-sign, 4H Momentum, and H-SW1 require implementation-level reconciliation before any executable-PnL claim.

Gate 0 PASS therefore means the contract and deterministic decision path are valid, not that any historical strategy is profitable. The next permission boundary remains: no new data capture or hypothesis discovery until representative historical implementations are reconciled against the v1.1 invariant.


## Gate 0.5 — Historical executable-PnL reconciliation — 2026-09-22

Gate 0.5 decision: GATE_0_5_PASS_WITH_PROXY_LIMITATION.

H-VOL1 is the representative historical implementation that satisfies the v1.1 executable-PnL invariant and reproduces its stored result deterministically: N=306, gross +1.4758597311 bps, net -8.5241402689 bps, stress -10.5241402689 bps, net CI95 [-14.9013323141, -2.1469482237]. It is therefore executable PnL evidence, but it is economically negative and does not qualify for profit promotion.

H-MR1 and H-BASIS1 reproduce their historical results but are classified as FORWARD_RETURN_PROXY because their historical fill semantics do not satisfy the executable invariant. H-FB3 is blocked because its cited executor artifact is not recoverable as a repository commit. H-FB1, H-FB2, Family D momentum, and H-SW1 retain implementation/data blockers.

No historical result satisfies the profit promotion gate. No historical result was overwritten or retuned. Trading remains OFF.

Authorized next action is data-foundation engineering only: preserve the executable-PnL engine, build immutable microstructure capture, audit OI/liquidation semantics, and collect observation-only data. No new hypothesis outcome is authorized.


## Hypothesis memory contract — 2026-09-22

A canonical **Hypothesis Record** is now required before any future hypothesis outcome is queried.

The record is persisted in Supabase table `public.research_hypothesis_records` and governed by `docs/HYPOTHESIS_RECORD_CONTRACT.md`. The dashboard is only a read-only presentation layer.

Each record preserves, where recoverable:
- origin type and source/reference;
- research question and rationale;
- mechanism;
- variables and exact equations;
- frozen parameters;
- entry/exit and invalid-data rules;
- cost model;
- validation/promotion gates;
- implementation/result/dataset lineage;
- final decision and provenance status.

Origin must be classified explicitly as `EXTERNAL_REFERENCE`, `INTERNAL_HYPERHAN`, `DERIVED_FROM_EXISTING_HYPOTHESIS`, `RESEARCH_RECOMBINATION`, or `NOT_RECOVERABLE_FROM_CURRENT_RECORD`. Agents must not infer or invent an external reference for a historical hypothesis.

The table is append-only at the row level. Corrections require a new `record_version`; update/delete mutations are rejected by database trigger. RLS is enabled and there is no public read policy. A future public dashboard surface must expose only a bounded, deliberate read model.

Initial historical records have been backfilled for H-MR1, H-VOL1, and H-BASIS1 from surviving project evidence. H-MR1 and H-VOL1 are recorded as internal-origin because their preregistrations explicitly describe them as new mechanisms with no external citation. H-BASIS1 origin remains `NOT_RECOVERABLE_FROM_CURRENT_RECORD`; the system does not guess its source.

This contract is a **memory/provenance improvement only**. It does not reopen hypothesis generation, change historical results, or alter the current research pause. Trading remains **OFF**.


## Historical data architecture — 2026-09-22

The project now records external historical datasets separately from raw storage. Supabase is **not** intended to become the raw historical-data warehouse.

Target flow:

external authoritative source / permitted archive -> immutable external/local archive -> research compute -> compact evidence/results -> Supabase

Supabase should retain dataset identity, provenance, checksums, research state, results, replay metadata and bounded dashboard state. Large raw candles, trades, order books, OI, liquidation and similar historical payloads should remain outside Supabase when practical.

A new append-only registry was applied to production:

`public.research_dataset_registry`

Migration:
`supabase/migrations/20260922193000_create_research_dataset_registry.sql`

The registry stores source URI, symbol/timeframe, period, storage class/location, checksum, provenance and redistribution status. It does not store raw market payloads. Update/delete are rejected; corrections require a new dataset identity/version.

External repository findings are preserved in:
`docs/HISTORICAL_DATA_FINDINGS_QUEUE.md`

Current findings are **queue-only**. No strategy was imported, no fork was made, and no external raw dataset was copied. Before any data extraction, source availability and redistribution terms must be verified.

Trading remains **OFF**.
