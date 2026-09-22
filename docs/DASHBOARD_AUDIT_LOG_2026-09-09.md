# Dashboard Audit Log — 2026-09-09

**Writer:** v0 session on `v0/modern-pro-dark-dashboard`
**Scope:** read-only dashboard cleanup after A–Z review

## Changes

- Removed the duplicate `get()` fetch helper from `dashboard/index.html`.
- Removed `localStorage` page persistence; navigation now defaults to Overview per page load and keeps state in memory only.
- Preserved the read-only boundary, existing endpoints, refresh cadence, H-FB1 decision, and H-SW1 frozen comparison path.

## Information architecture rewiring

- Restored `Story` as the first page and landing surface.
- Renamed `Overview` to `Terminal` in the public navigation.
- Returned owner identity `@parhanfirdausnugraha` to the header and footer.
- Surfaced H-SW1 frozen comparison in Terminal with backend-only values and explicit unavailable copy.
- Kept Visual focused on derived observations and honest insufficient-evidence states.
- Preserved read-only execution boundary and existing endpoint contract.

## Verification boundary

- No database, Supabase schema, environment variable, endpoint, research result, or trading behavior was changed.
- The older Visual iOS CSS remains present as legacy source overridden by the modern research-console rules; a future dedicated CSS extraction can remove it safely.
- Browser/runtime verification remains required after the final commit; this writer does not mark the dashboard independently verified.

## Evidence

- Changed file: `dashboard/index.html`
- Coordination checkpoint updated in `docs/SYNC_CHECKPOINT_2026-09-09.md`
- Status: `claimed_done`, pending independent verification


## Owner-first total refresh — 2026-09-09

**Writer:** Manus
**Scope:** owner-facing dashboard surface, landing entry point, and static contract tests
**Commit:** `b416ae01fb2e475e85357672b5c141fe46d273b4`

### Synchronization basis

Before editing, GitHub `main`, Supabase project `xaqsntunrqvqpzlbeutt`, the experiment ledger, the live-only dashboard policy, and the coordination ledger were inspected. No research migration, RPC, result row, execution path, or API contract was changed. The active writer lock was recorded in `public.agent_coordination_log` as `dashboard-owner-first-total-refresh-2026-09-09`.

### Surface changes

The dashboard now presents Story, Terminal, and Visual as three owner-facing surfaces. Story is the briefing page, Terminal is the research record, and Visual is the observation view. The presentation was rebuilt with a restrained dark archive language: no gradients, no neon glow, no agent/model branding, explicit status labels, fixed `en-US` numeric formatting, and clear `UNAVAILABLE` / `no value fabricated` states. H-FB1 remains `KILL`, H-SW1 remains `INCONCLUSIVE`, and execution remains `OFF`.

The legacy `/lab` entry point now redirects to the canonical dashboard instead of presenting a second inconsistent landing experience.

### Verification evidence

The repository validator passed, dashboard JavaScript passed `node --check`, and the full local suite passed with `53 passed, 2 skipped`. The production read-only endpoints returned live responses for `/health`, `/api/v1/market/ohlcv/latest`, `/api/v1/funding/latest`, and `/api/v1/signals/log`. The production deployment/runtime after this commit still requires an independent post-deploy check; local validation is not marked as independent verification.


## Final runtime gap closure — 2026-09-19

**Writer:** Manus
**Scope:** dashboard runtime integrity only; no Supabase schema, research result, hypothesis parameters, or execution path changed.

The current main dashboard was independently reviewed against the live Supabase readiness payloads. Two concrete defects were found: the dashboard runtime attempted to call outcome RPCs for H-MR1 and H-VOL1 even though both are `NOT_READY / outcome_run=false / authorization not granted`, and the Binance read-only script contained a malformed JavaScript literal that prevented the second script block from parsing. The fix changes both hypothesis cards to call readiness RPCs only, renders backend-derived readiness facts without profitability metrics, and restores the Binance public ticker assignment.

Local evidence after the fix: `68 passed, 2 skipped`; both dashboard script blocks pass `node --check`; readiness-only and Binance runtime guards pass; `git diff --check` passes. The two skipped tests are existing Supabase service-role integration tests unavailable in this environment. Live Supabase evidence remains `H-MR1 NOT_READY` and `H-VOL1 NOT_READY`, with 84 missing minutes, no OOS boundary, no outcome run, and no authorization. No result was changed or newly computed.

Production was independently observed before this patch at Vercel deployment `dpl_DVeUecUWovENNHaNnDq9fvLjDLmb`, state `READY`, source commit `b0b12bf6eb27ed258b2875f36b3b6c8515e9bb8d`. Post-push verification must confirm the new commit and browser runtime before this batch can be marked verified.


## Registry visibility fix — 2026-09-20

The post-deploy browser check exposed a real owner-facing mismatch: Supabase contained eight rows in `research_hypotheses`, but the public REST read returned zero rows because the table had RLS enabled without a SELECT policy. The dashboard consequently displayed `0 REGISTERED`, which was false as an inventory statement. Migration `20260919221500_research_hypotheses_public_read.sql` adds a SELECT-only policy for `anon` and `authenticated`, grants only SELECT, and explicitly revokes write privileges. No result data, execution permission, or hypothesis mutation path was opened.

Live verification after applying the migration: public REST returned HTTP 200 and `8` hypothesis rows. Local evidence after adding the regression guard: `69 passed, 2 skipped`; dashboard JavaScript and readiness-only guards passed. Source was pushed in commit `d16c6011b04a9581bfa0c97b5b8d977cb7fd040f`.


## Provider-state and live integrity correction — 2026-09-20

**Writer:** Manus
**Scope:** owner-facing dashboard presentation and evidence labeling only; no outcome scan, order path, result mutation, or research-method change.

A final source audit found two stale provider labels in the infrastructure room: Vercel was still shown as `BUILDING*` at obsolete commit `e5110aa`, while Railway was shown as `FAILED*` even though the provider console was not readable in this verification session. The dashboard now labels the last independently observed Vercel deployment `READY · OBSERVED` at commit `d16c601` and labels Railway `UNVERIFIED`; it makes no unsupported health claim for Railway. The provider footer now explicitly distinguishes evidence snapshots from live provider APIs.

Live read-only checks remained consistent with the dashboard boundary: Supabase returned 141,772 OHLCV rows, 10,510 basis snapshots, 288 funding events, and 8 registered hypotheses. `collector_health` most recently reported `feed_status=connected`, `integrity_status=valid`, zero sequence gaps, `latency_ms=35`, and `contamination_active=false` at its recorded update. Supabase `pg_proc` also confirms that `research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric)` exists in production; the older coordination note claiming it was absent is stale and should not be treated as current. No H-MR1 outcome scan was invoked.

Validation evidence: `check_dashboard_js.py` passed; `validate_readiness_runtime.py` passed; `PYTHONPATH=src pytest -q` returned 70 passed and 2 skipped; `git diff --check` passed. The two pytest warnings are pre-existing unknown `integration` markers in `tests/test_supabase_research.py` and do not indicate a test failure.

The change remains bounded to `dashboard/index.html`, `tests/test_dashboard.py`, and this append-only audit record. Deployment verification for the new commit remains a separate release step.


## Release verification — final commit c2bedd9 — 2026-09-20

Vercel production deployment `dpl_BiGpJC66AtjrgaV5qC7ttBQgHqqL` for full commit `c2bedd9a7c8c32b781ce10b6aee49a9644f6d7f1` reached `READY` and was observed under the production target. Canonical `https://btc-usdt-research2.vercel.app/` returned the corrected `READY · OBSERVED` and `UNVERIFIED` provider labels, no `BUILDING*` or `FAILED*` markers, and the read-only H-VOL1 readiness endpoint returned `NOT_READY` with `outcome_run=false`. Browser verification showed the dashboard reached `LIVE`, rendered 8 registered hypotheses and live collector facts, and the browser console had no output/errors.

Railway remains intentionally labeled `UNVERIFIED`: the Railway console did not expose readable service state in this session, so the dashboard does not claim healthy or failed. This is the final evidence boundary for this release.


## Canonical archive bindings on remote main — 2026-09-22

Remote `main` advanced to `b3ae942` with concurrent Gate R2, provenance, hypothesis-record, dataset-registry, and external-source architecture work. The earlier local commit was preserved on backup branch `manus/archive-office-c61` rather than force-pushed. Only the missing owner-facing bindings were ported onto the remote state: dataset registry metadata, canonical hypothesis records, and a bounded public coordination summary view. Existing no-scan, backoff, research-gate, and trading-OFF behavior was preserved.

Migration `20260922203000_public_read_research_archive_views.sql` is SELECT-only for anonymous/authenticated readers and revokes public write operations. The dashboard shows the honest empty dataset state and canonical records without importing raw historical data or external strategies. Validation on the reconciled remote tree: JavaScript check passed; **80 tests passed, 2 skipped**; two pre-existing integration-marker warnings remain.
