# Project Forensic Review — 2026-09-22

## Scope

This review is a project-level forensic checkpoint, not a new trading hypothesis. It was executed after the synthetic validation harness `HARNESS-2026-09-22` passed 4/4 decision-path tests.

The question is:

> Can the current BTCUSDT research system produce a result that is not only statistically calculated, but also sufficiently trustworthy as executable trading evidence?

Trading remains OFF.

## Evidence inspected

- `AGENTS.md`
- `docs/EXPERIMENT_LEDGER.md`
- Supabase `agent_coordination_log`
- Supabase schemas and live research functions
- Supabase `research_results`
- Supabase data counts and time coverage
- Supabase migration registry
- synthetic validation harness result

## 1. Data layer — material limitation

Live counts:

- `ohlcv_1m`: 141,772 rows
- OHLCV coverage: 2026-06-03 through 2026-09-09
- previously audited missing minutes: 84
- `funding_rate_events`: 288 rows
- `funding_basis_snapshots`: 10,510 rows
- `feature_snapshots`: 0 rows

Implications:

1. The OHLCV dataset is usable for short-horizon research, but it is not a long regime history.
2. Funding/basis data is materially shorter in active coverage than OHLCV.
3. Feature-snapshot infrastructure exists in schema but has no stored rows, so it cannot currently support claims based on persistent microstructure feature history.
4. A hypothesis requiring OI, liquidation flow, or another absent field cannot be honestly tested from the current dataset.

Finding: **DATA-SUFFICIENT for bounded OHLCV experiments; DATA-INCOMPLETE for broader market-state research.**

## 2. Feature layer — not yet fully proven

The project has real OHLCV fields including taker-buy volume and quote volume, plus basis/funding fields. However, the forensic record shows repeated concern around timestamp alignment, availability at decision time, and exact window construction.

The synthetic leakage test passed, which validates the decision-path test itself. It does not prove every production research RPC is leakage-free.

Finding: **PARTIALLY VERIFIED. Production RPCs require function-level independent replay for any future promoted result.**

## 3. Hypothesis layer — architecture debt

The migration registry contains a large sequence of research revisions, repairs, fast paths, type fixes, and public bridges. H-MR1 and H-VOL1 each accumulated multiple implementation migrations.

The live database currently contains multiple related functions for H-MR1/H-VOL1 and two H-SW1 functions with different signatures:

- H-SW1 text-typed frozen function
- H-SW1 Manus bigint-typed function

The existence of multiple implementations is not itself proof of an incorrect result. It is, however, a reproducibility hazard unless every official result identifies the exact function identity/signature and source lineage.

Finding: **LINEAGE RISK — HIGH.**

Required rule for the next cycle: one hypothesis identity -> one frozen implementation identity -> one result lineage. Repairs must create explicit version lineage rather than silently becoming the current method.

## 4. Economics / execution layer — needs stronger evidence

The project consistently declares a 10 bps round-trip baseline and 12 bps stress model. That is good governance, but the forensic review must distinguish:

- proxy return vs executable entry/exit price,
- fee vs slippage,
- latency,
- funding cashflow,
- overlap/non-overlap,
- exact timestamp of signal availability,
- exact timestamp/price of fill.

A positive proxy result would not be enough to promote a future candidate unless the execution mapping is reproducible.

Finding: **COST GOVERNANCE EXISTS; EXECUTABLE-PNL PROOF IS NOT YET A project-wide invariant.**

## 5. OOS / statistics — mixed evidence quality

Persisted results show repeated negative economics:

- H-FB3: net EV about -10.12 bps, CI entirely negative.
- Family D 4h momentum: net EV about -14.87 bps, CI entirely negative.
- H-MR1: net EV about -3.03 bps, CI crosses zero.
- H-VOL1: net EV about -8.52 bps, CI entirely negative.
- H-SW1: +4.73 bps net point estimate, but CI [-45.21, +54.68] and period instability; not promoted.
- H-BASIS1 mechanism scans: negative net proxy across tested horizons and only 3 active OOS days.

This pattern does not prove that no market edge exists. It does show that the available evidence has not produced a validated edge.

The bigger statistical concern is evidence breadth: some mechanisms have too few independent calendar days/regimes to support strong claims even when trade count is large.

Finding: **NO PROMOTION EVIDENCE. OOS design is directionally sound but data breadth remains a bottleneck.**

## 6. Agent workflow — concrete process debt

The coordination log contains many stale `proposed` tasks and at least one old `in_progress` task. The current contract says stale tasks should be superseded/locked during handoff, but the live ledger still contains historical unresolved states.

More importantly, prior independent audits found real mismatches:

- H-MR1 was once reported with an RPC that an independent audit found missing; later repair migrations now make the function exist.
- H-FB3 had a dashboard stress-value mapping defect discovered by independent verification.
- Historical H-SW1 implementation work produced a signature/logic collision that would have silently created a different overloaded function.
- Several implementation claims were verified only after another agent challenged them.

These are exactly the kinds of failures the executor/verifier rule is intended to catch.

Finding: **AGENT GOVERNANCE EXISTS ON PAPER, BUT ENFORCEMENT/STATE HYGIENE HAS NOT BEEN RELIABLE ENOUGH.**

## 7. Synthetic harness result

`HARNESS-2026-09-22` passed:

- known positive synthetic edge -> PASS
- below-cost edge -> KILL
- look-ahead/leakage -> REJECT
- train-only edge failing OOS -> KILL

This means the decision-path harness behaves as intended. It does not validate every production research implementation.

## Forensic verdict

**The research engine is not proven broken.**

But the project is **not yet clean enough to justify another hypothesis cycle**.

The dominant problem is no longer “we need another clever edge.” The dominant problem is **trustworthiness of the research pipeline**:

1. data breadth is limited,
2. feature availability is incomplete,
3. implementation lineage has become complex,
4. executable-PnL semantics are not yet a project-wide invariant,
5. OOS evidence is often short in independent time,
6. agent-state/verification hygiene has accumulated debt.

## Required next gate

Before another hypothesis:

1. Freeze one canonical implementation per historical result.
2. Mark or lock stale coordination tasks.
3. Build a result-lineage manifest mapping hypothesis -> preregistration -> function -> migration -> result -> verifier.
4. Independently replay at least one representative killed result and one inconclusive result from the canonical function.
5. Establish an explicit executable-PnL contract.
6. Establish a minimum independent-time requirement for promotion, not only trade count.
7. Keep synthetic harness tests as regression tests.
8. Only then decide whether the dataset is worth another research cycle.

**Decision: PAUSE NEW HYPOTHESES.**

Historical evidence remains append-only. No failed result is retuned. Trading remains OFF.
