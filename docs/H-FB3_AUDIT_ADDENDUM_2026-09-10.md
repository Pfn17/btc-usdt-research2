# H-FB3 Audit Addendum — Five Gap Closure

**Date:** 2026-09-10  
**Scope:** H-FB3 public result, dashboard presentation, and research-governance trace  
**Result integrity:** The persisted H-FB3 result is unchanged.

## 1. Stress value rendering

The public API stores the 12 bps round-trip stress result at `evidence.stress_net_bps`. The dashboard previously checked the nonexistent `evidence.parameters.stress_rt_bps` field, causing a false `UNAVAILABLE` state. The render path now reads the persisted stress value directly and displays `-12.119 bps` from the live payload. No value is recalculated in the browser.

## 2. EV/CI comparison coverage

The research comparison chart now contains four rows: H-FB1, H-FB3, H-SW1 reference, and H-SW1 independent. H-FB3 uses the same persisted mean and 95% confidence interval returned by `/api/v1/research/hfb3`; it is not inferred from the decision label.

## 3. Discarded N=4,692 run

An append-only audit record has been added to the coordination ledger for the earlier **N=4,692** run. That run is retained as a discarded execution trace, not as evidence and not as an alternative result. The recorded reason is a wrong OOS timestamp window. It was superseded by the frozen complete-day window **2026-08-03 00:00:00 UTC through 2026-09-09 23:59:59.999 UTC**. The official result remains the later N=2,984 run persisted in `research_hfb3_public`.

## 4. Frozen OOS window reconciliation

The exact frozen preregistration is available in GitHub commit `fd712a286f4ef79476da11dcf985a8650c7008eb`, `docs/H-FB3_PREREGISTRATION.md`. It explicitly records:

- OOS start: `2026-08-03T00:00:00Z`;
- OOS complete-day end: `2026-09-09T23:59:59.999Z`;
- query cutoff: `2026-09-10T10:18:00Z`;
- dataset SHA-256: `fc50dad316294d51f4dcde2a1d08b6450d4561cd2d9353717f1f7bfe2b215947`;
- specification SHA-256: `d30dc52492e5b84c2d0cf1cddededc2b1414a5a3649ace226ba092d7b0208b6d`.

The window matches the final H-FB3 execution trace. This closes the verification gap without changing the frozen specification.

## 5. Multiple-testing / FDR policy

The project policy is now explicit for future confirmatory batches:

1. Every confirmatory hypothesis family must declare its testing family, hypothesis universe, and FDR procedure before its first outcome is opened.
2. The default procedure is Benjamini–Hochberg at `q = 0.05` across the predeclared confirmatory family. Exploratory scans are labelled exploratory and cannot be promoted as confirmatory findings.
3. A result must still pass its own frozen economic, temporal, cost, and confidence gates. FDR adjustment cannot rescue a failed result.
4. H-FB3 remains an archived **unadjusted pre-registered KILL** because its net EV is negative and its CI95 is entirely below zero. No retroactive FDR correction is applied to change or relabel the historical outcome.
5. No H-FB4 or later confirmatory outcome may be opened until its family registry and FDR declaration are recorded first.

This policy closes the governance gap prospectively while preserving the historical H-FB3 record exactly as run.

## Evidence boundary

The H-FB3 result remains:

- `n = 2,984`;
- net EV `-10.118565 bps`;
- CI95 `[-10.793438, -9.443693] bps`;
- stress net EV `-12.118565 bps`;
- status `KILLED`;
- `trading_enabled = false`.

No rerun, retune, migration, RPC modification, or execution activation was performed as part of this addendum.
