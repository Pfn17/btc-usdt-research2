# H-BASIS1 Provenance Recovery Report

## Executive finding

**Status: PROVENANCE RESTORED.** The historical H-BASIS1 result with `N=156` is reproducible from the exact analysis implementation committed in Git at `5146f6ab173fad888e23558234822627ce801a30`. Replaying that file against the frozen raw extract reproduces the stored primary 15-minute OOS result exactly, including sample count, gross return, net return, stress return, convergence rate, and both primary confidence intervals.

The current Supabase RPC `public.research_funding_basis_scan_frozen(bigint, integer, integer, numeric, numeric)` is not the historical H-BASIS1 implementation. Its semantics are a funding-delta/basis-delta agreement scan, and its latest-cutoff output contains agreement counts `7,412` and `2,862`. It must remain unchanged. The prior lineage row recording this mismatch is preserved. A new append-only lineage row records the recovered implementation identity and exact replay.

No production RPC was replaced. No historical result was edited, deleted, or overwritten. Trading remains **OFF**.

## Historical result identity

The immutable historical result is:

- `result_id`: `907bf0bb-9ed5-4456-94ce-cf8dda2b5e26`
- `sample_count`: `156`
- model run: `6be0f00d-99d8-4226-a4a6-bd7e787270c6`
- model name: `H-BASIS1_MECHANISM_H15`
- batch: `hbasis1-mechanism-20260921`
- batch ID: `7d129e25-0e88-47f9-98a0-03e474cf02f7`
- stored status: `inconclusive_underpowered`
- created at: `2026-09-21 13:32:52.143965+00`

The historical result remains unchanged in `public.research_results`. A direct read confirmed exactly one row for this result ID.

## Historical implementation identity

The recovered implementation is a Python research script, not the current SQL RPC:

- repository path: `scripts/analyze_hbasis1_mechanism.py`
- historical commit: `5146f6ab173fad888e23558234822627ce801a30`
- commit subject: `research: preregister and analyze H-BASIS1 basis convergence`
- commit timestamp: `2026-09-21T13:31:39Z`
- exact historical script SHA-256: `1614afcd8217c7820d9022b1014a063cd0dff6d7f658573d66ef000c2a8e5109`
- implementation entry point: module execution with `HBASIS1_RAW`; event construction is `build_events(horizon_min)`
- implementation semantics: six-hour prior elapsed-time median basis baseline, train-only absolute residual P90 threshold, one-minute entry delay, greedy non-overlap by scheduled exit, actual-timestamp forward matching, residual convergence at 50% of entry magnitude, and mark-price directional proxy returns.

The later commit `458574f785cef9d697a2a646f7b835092897c7f8` added predeclared 12-hour and 48-hour bootstrap sensitivity fields. It did not change the primary event construction or the primary 15-minute result. The exact replay below was nevertheless run from the earlier historical commit, not from the later file.

## Migration and database lineage

The database migration history contains the funding-basis source-table and SQL scan migration:

| Migration | Role | Relevance to historical H-BASIS1 |
|---|---|---|
| `20260903032336_funding_basis_snapshots_and_frozen_scan` | Created `public.funding_basis_snapshots` and the predecessor/current frozen funding-basis scan path | Data-source and predecessor lineage only; it does not implement the six-hour residual event study |
| `20260903043515_funding_hfb1_rpc` | H-FB1 funding-event RPC | Separate hypothesis family; not used for H-BASIS1 |
| `20260921173635_20260922_forensic_gate_lineage_pnl_regression` | Added forensic lineage and regression-gate infrastructure | Audit infrastructure; not the historical event implementation |

No H-BASIS1-specific SQL migration or historical SQL function matching the Python residual-event semantics was found in the repository or in the migration names exposed by Supabase. The exact historical implementation is therefore identified as the Python script in commit `5146f6a`, while the funding-basis table migration is recorded as its data-source predecessor.

## Parameter reconstruction

All parameters below were taken from the frozen preregistration, freeze artifact, stored model-run parameters, or the historical script. None was selected from the replay output.

| Parameter | Reconstructed value |
|---|---|
| Source table | `public.funding_basis_snapshots` |
| Symbol | `BTCUSDT` |
| Dataset rows | `10,510` |
| Dataset hash | `3ce9038421d76c3bf077dc3f5e3261a25311670286cca3801d90f113be470d79` |
| First timestamp | `2026-09-03T04:34:56Z` |
| Query cutoff / last timestamp | `2026-09-10T18:16:03Z` (`1789064163000`) |
| Train end | `2026-09-07T23:59:59.999Z` (`1788825599999`) |
| OOS start | `2026-09-08T00:00:00Z` (`1788825600000`) |
| Baseline | Median of prior elapsed six hours |
| Minimum baseline observations | `30` |
| Threshold | Train-only absolute residual P90; frozen value `1.551082 bps` |
| Entry delay | `1 minute` to first actual timestamp at or after the target |
| Primary horizon | `15 minutes` |
| Exit tolerance | `2 minutes` after scheduled target |
| Overlap rule | Greedy chronological events; next signal cannot precede the scheduled prior exit |
| Convergence | `abs(exit residual) <= 0.5 * abs(entry residual)` |
| Direction | `LONG` for negative entry residual; `SHORT` for positive entry residual |
| Return proxy | Directional mark-price return in basis points |
| Baseline cost | `10 bps` round trip |
| Stress cost | `12 bps` round trip |
| Bootstrap | 2,000 resamples, UTC-day event blocks, seed `20260921`, empirical percentile interval |

## Replay method

The replay used the raw extract created by the historical extraction procedure. The extract contains the five canonical fields used by the script: `symbol`, `server_time_ms`, `mark_price`, `index_price`, and `basis_bps`. Its semantic dataset hash is the frozen hash above. The raw JSON file SHA-256 was `140f8fd10eb876f0499ada3e7704ed78fe0ee6c8d8830c02d130eb8357072887`.

The exact script was recovered with `git show 5146f6a:scripts/analyze_hbasis1_mechanism.py` and run without edits against `/tmp/hbasis1_raw.json`. The replay output was compared to the committed analysis artifact at the primary 15-minute event-row level and summary level. The event rows matched exactly, not only the aggregate N.

## Historical versus replay

| Field | Historical stored result | Exact replay | Match |
|---|---:|---:|:---:|
| Primary OOS N | 156 | 156 | YES |
| Active OOS UTC days | 3 | 3 | YES |
| Gross mean | −1.0956948753997517 bps | −1.0956948753997517 bps | YES |
| Net mean | −11.09569487539975 bps | −11.09569487539975 bps | YES |
| Stress mean | −13.09569487539975 bps | −13.09569487539975 bps | YES |
| Net CI95 low | −13.526151211184727 bps | −13.526151211184727 bps | YES |
| Net CI95 high | −8.55302646754086 bps | −8.55302646754086 bps | YES |
| Convergence count | 53 of 156 | 53 of 156 | YES |
| Convergence rate | 0.33974358974358976 | 0.33974358974358976 | YES |
| Convergence CI95 low | 0.1987179487179487 | 0.1987179487179487 | YES |
| Convergence CI95 high | 0.4807692307692308 | 0.4807692307692308 | YES |
| Median time to convergence | 2.024983333333333 min | 2.024983333333333 min | YES |
| Censored exits | 0 | 0 | YES |

The stored result's `expectancy`, `cost_adjusted_ev`, `hit_rate`, `confidence_interval`, `bootstrap`, `regime_stability`, and `period_concentration` fields agree with the replay summary. The stored row was not changed.

## Current RPC mismatch

The current RPC was inspected directly from PostgreSQL. Its signature is `research_funding_basis_scan_frozen(bigint, integer, integer, numeric, numeric)`. Its source computes one-step funding and basis deltas, groups by same-sign agreement, uses a forward mark lookup, and does not compute a local six-hour residual, train-only P90 threshold, greedy event non-overlap, or convergence event label.

At the latest stored snapshot cutoff with a 15-minute horizon and the current cost arguments, it returned:

| Current RPC output group | Count |
|---|---:|
| `agreement = 0` | 7,412 |
| `agreement = 1` | 2,862 |

This mismatch is expected from the source-definition difference. The current RPC remains the current production implementation for its own scan and was not replaced or modified.

## Conclusion and controls

The historical provenance chain is now restored to the level required for independent verification: frozen preregistration, frozen dataset identity and cutoff, exact Git implementation, linked database result metadata, and exact replay agreement. The correct status is **PROVENANCE RESTORED**, not a new research outcome or a trading approval.

No parameter retuning was performed. No parameter search was performed. No new hypothesis was introduced. The historical result `907bf0bb-9ed5-4456-94ce-cf8dda2b5e26` was not modified. The previous `MISMATCH` lineage row was not overwritten; a new append-only `MATCH` manifest row records the recovery. No production RPC was changed. Trading remains **OFF**.

CG4 should perform the independent verification and decide any regression-gate outcome. This report does not claim a regression-gate pass and contains no trading recommendation.

## References

[1]: https://github.com/Pfn17/btc-usdt-research2/commit/5146f6ab173fad888e23558234822627ce801a30 "Historical H-BASIS1 implementation commit"
[2]: https://github.com/Pfn17/btc-usdt-research2/blob/main/docs/H-BASIS1_PREREGISTRATION.md "H-BASIS1 frozen preregistration"
[3]: https://github.com/Pfn17/btc-usdt-research2/blob/main/docs/H-BASIS1_MECHANISM_REPORT_2026-09-21.md "H-BASIS1 mechanism report"
[4]: https://github.com/Pfn17/btc-usdt-research2/tree/main/supabase/migrations "Repository migration directory; Supabase-only migration versions are identified by database metadata in this report"

[1] [2] [3] [4]
> Internal database evidence is identified by its immutable UUIDs, migration versions, and exact query results in this report. Supabase result and migration records are not publicly linked.
