# Research State — 2026-09-02

## Single source of truth

Implementation state is determined from Git commit/tree. Database state is determined from live Supabase migrations, schema, and query results. `claimed_done` is not `verified`.

## Data state

- `ohlcv_1m`: 129,785 BTCUSDT 1m rows at last verification.
- Historical span: ~90 days.
- OHLCV gap audit: 0 gaps greater than 1 minute.
- Latest OHLCV candle is live/fresh.
- L2 `feature_snapshots`: live collection healthy.
- Live trading: **OFF**.

## Combined implementation

Migration:

`supabase/migrations/20260902_combined_alpha_and_signal_audit.sql`

Status: **APPLIED + VERIFIED**

Supabase migration version:

`20260902090528_combined_alpha_and_signal_audit`

Objects verified:

- `public.signal_audit_events`
- `public.research_combined_alpha_scan_frozen(bigint,integer,integer,integer,integer,numeric,numeric)`

## Frozen hypothesis H-C1

**L2 imbalance + same-sign most-recent CLOSED 1m candle momentum**

- signal: imbalance Q20/Q80 from pre-test data only
- LONG: imbalance >= Q80 and closed 1m candle return > 0
- SHORT: imbalance <= Q20 and closed 1m candle return < 0
- horizon: 60s
- purge: 60s
- embargo: 60s
- no threshold sweep
- no ML

## First live database run

Cutoff: latest feature event at verification time.

Sample: 50,000 entries, producing four OOS test folds (folds 2–5).

Fee/slippage run at 0/0 bps was executed directly against Supabase.

| Fold | Signal N | Signal rate | Gross EV (bps) | Net EV (bps) | CI95 low |
|---|---:|---:|---:|---:|---:|
| 2 | 2,424 | 24.24% | -0.116 | -0.129 | -0.307 |
| 3 | 2,218 | 22.18% | +1.999 | +1.986 | +1.796 |
| 4 | 1,922 | 19.22% | +1.221 | +1.208 | +0.970 |
| 5 | 2,172 | 21.72% | -0.128 | -0.142 | -0.388 |

Result: **REJECT H-C1 for promotion**. Two of four OOS folds are negative even before trading fees. This is not a validated edge.

Do not rerun H-C1 with alternative thresholds, horizons, or directions merely to search for a green result. A new experiment must be a separately stated hypothesis.

## Signal audit journal

`signal_audit_events` exists in Supabase, but runtime event writing and dashboard history/unseen UI are **NOT YET VERIFIED/COMPLETE**. The table currently contains 0 events.

Required next implementation for monitoring:

1. Persist candidate/rejected/paper state transitions from the authoritative signal path.
2. Add `/api/v1/signal/history` (recent events + count since supplied timestamp).
3. Add dashboard `UNSEEN EVENTS` / `LAST EVENT` so the operator does not need to watch continuously.

## Next research rule

The combined paradigm remains active, but H-C1 is rejected. Do not modify the rejected hypothesis. Define one new mechanism using L2 + OHLCV, preregister it, implement it, run frozen OOS, then independently verify.

Live order placement remains disabled until a mechanism passes all promotion gates and forward paper validation.
