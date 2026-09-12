# Agent Handoff — H-VOL1 Readiness Implementation — 2026-09-12

**Writer:** Manus
**Status:** implemented / readiness visible / awaiting independent audit
**Scope:** H-VOL1 preregistration, source reconciliation migration, manual API route, owner-facing readiness card, contract tests, and audit trail.
**Outcome scan:** intentionally not run.
**Execution:** disabled; no order or paper-promotion path added.

## Existing live registry reconciled

Supabase already contained the H-VOL1 registry and live objects before this GitHub batch:

| Object | Live fact |
|---|---|
| Family | `fam-vol-v1` |
| Protocol | `v1-fdr-q005` |
| Hypothesis | `H-VOL1` |
| Frozen registry status | `FROZEN_IMPLEMENTED_UNRUN` |
| Live readiness RPC | `public.research_hvol1_readiness(bigint,bigint)` |
| Live manual scan RPC | `public.research_hvol1_scan_frozen(bigint,bigint,numeric,numeric,numeric)` |
| Live migration registry | `20260912075810`, `20260912075927`, `20260912080008` |

Those three live migration names were not present in the GitHub `main` checkout. The new `20260912100000_hvol1_source_reconciliation.sql` file therefore records the object definitions under a new source-reconciliation migration instead of pretending to be one of the historical migrations. It is not a second hypothesis or a second scan path.

## Readiness evidence

A read-only call to `research_hvol1_readiness(1789064160000, NULL)` returned:

| Field | Value |
|---|---:|
| `status` | `NOT_READY` |
| coverage | `141,772` candles from `1780552860000` to `1789064160000` |
| expected minute count | `141,856` |
| missing minutes | `84` |
| continuity | `false` |
| complete 120-minute range windows | `141,065` |
| valid taker ratios | `141,772` |
| training/OOS candles | `0 / 0` because no cutoff was supplied |
| train P90/P10 | not computed because no cutoff was supplied |
| outcome | `false` / UNRUN |
| authorization | `NOT GRANTED` |

This is data readiness, not profitability evidence. No result row exists for H-VOL1.

## Owner-facing implementation

The dashboard now polls only `/api/v1/research/hvol1/readiness`. It displays continuity, range-window coverage, valid taker-ratio count, train/OOS state, P90/P10 state, exact boundary state, entry/exit availability, non-overlap method, cost assumptions, outcome state, and authorization state. It does not poll `/api/v1/research/hvol1`, choose an OOS cutoff, or preview profitability.

The manual route `/api/v1/research/hvol1` is present for a future authorized run but remains outside dashboard polling and returns `authorization: NOT GRANTED` with `trading_enabled: false`.

## Verification boundary

Writer-side validation passed: `65 passed, 2 skipped`; dashboard JavaScript passed `node --check`. The two skipped tests are the existing Supabase integration tests without service-role credentials. Independent verification must still review the source reconciliation migration against the live RPC definitions, especially strict range-window timestamp checks, exact entry/exit alignment, greedy previous-accepted-exit non-overlap, train-only P90/P10 scope, and the fact that no outcome was queried.

## Explicit next action

Do not freeze an OOS cutoff or execute H-VOL1 until an independent verifier signs off on the migration/API/dashboard contract and the owner records the exact cutoff decision. If the 84 missing minutes affect the eligible window, the verifier must decide how the predeclared invalid-window rule applies; no silent gap repair is allowed.
