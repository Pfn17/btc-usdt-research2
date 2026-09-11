# Agent Handoff — H-MR1 Implementation — 2026-09-11

**Writer:** Manus  
**Status:** claimed_done / awaiting independent verification  
**Scope:** preregistration, read-only Supabase RPC, manual API route, tests, ledger entry  
**Frontend:** intentionally unchanged  
**Outcome scan:** intentionally not run

## Implementation

H-MR1 is frozen as a new reversal hypothesis: a train-only 95th percentile of absolute 15-minute close-to-close return triggers an opposite-direction trade with a one-hour horizon. The implementation uses the explicit OOS cutoff supplied by the caller, chronological non-overlap, a 10 bps baseline cost, a 12 bps stress cost, and overall/weekly/direction output rows.

Git files:

- `docs/H-MR1_PREREGISTRATION.md`
- `supabase/migrations/20260911090000_hmr1_extreme_mean_reversion.sql`
- `src/btc_research/api.py`
- `tests/test_hmr1_contract.py`
- `docs/EXPERIMENT_LEDGER.md`

Supabase object applied:

`public.research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric)`

API route:

`GET /api/v1/research/hmr1`

The route is manual and research-only. It is not called by the dashboard and cannot place orders.

## Verification boundary

Local validation passed: `56 passed, 2 skipped`. This is writer-side evidence only. An independent verifier must inspect the SQL semantics, especially percentile training scope, fill alignment, non-overlap selection, weekly counts, and cost stress before any H-MR1 scan is executed.

No outcome, signal, PASS, KILL, or profitability claim exists yet. The expected pre-scan state is **FROZEN / IMPLEMENTED / UNRUN**.
