# Hypothesis Registry — Canonical Memory

The canonical structured records live in Supabase table:

`public.research_hypothesis_records`

The repository contract is:

`docs/HYPOTHESIS_RECORD_CONTRACT.md`

The experiment ledger remains the chronological project record:

`docs/EXPERIMENT_LEDGER.md`

The result-lineage manifest remains the implementation/result provenance record:

`docs/RESULT_LINEAGE_MANIFEST_2026-09-22.md`

## Authority

The structured Hypothesis Record is the canonical memory of:

- origin;
- rationale;
- mechanism;
- equations;
- frozen parameters;
- validation contract;
- lineage;
- decision.

The dashboard is a read-only view over approved evidence. It must not invent missing provenance.

## Historical backfill rule

Historical hypotheses are backfilled only from surviving repository/database evidence.

If origin, formula, or implementation details cannot be established, the record says so explicitly:

`NOT_RECOVERABLE_FROM_CURRENT_RECORD`

No agent may infer an external citation, author, or mathematical rule merely because it appears familiar.

## Current migration state

The initial table is append-only at the row level. Updates/deletes are rejected by database trigger. Corrections are new `record_version` rows.

RLS is enabled with no public read policy. Public presentation must use a deliberately bounded read surface rather than exposing the canonical research memory directly.
