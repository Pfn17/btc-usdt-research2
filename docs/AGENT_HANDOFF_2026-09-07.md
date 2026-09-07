# Agent Handoff — 2026-09-07

## Writer identity

This repository update was implemented by **Manus** in task `jrm7h7ztqAaCAkoaiTAxTM`. GitHub write access was verified by a successful push to `Pfn17/btc-usdt-research2`.

The implementation window was 2026-09-07 UTC. The repository branch was `main`. The database was not modified because Supabase MCP authentication was unavailable in the writer session and the supplied database connection string did not contain a password.

## Evidence commits

| Commit | Scope |
|---|---|
| `c579985` | Added Supabase recovery runbook and credential-safe backup exporter |
| `1ee5600` | Clarified dashboard research status and added portfolio identity |
| Current handoff | Added funding backfill driver, free-tier OHLCV guard, and this handoff record |

## Work completed in this handoff

The funding backfill driver at `src/btc_research/funding_basis/backfill.py` fetches completed Binance funding events oldest-first, paginates with a progress guard, and writes through the existing idempotent `funding_rate_events` upsert contract. It requires `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` when run against Supabase. It does not change any research rule.

The OHLCV one-shot utility now has a 257-day free-tier storage guard. This is an infrastructure budget constraint, not an H-SW1 parameter. No historical backfill was executed by this handoff.

The dashboard remains read-only. It reports observed funding direction, H-FB1 `KILL`, funding family `CLOSED`, and trading `DISABLED`. It does not report a swing signal.

## Swing research boundary

Swing trading is recorded as a **new research direction, not a validated strategy**. No H-SW1 implementation, query, signal, or result was created in this handoff because the complete frozen specification is not present in the repository.

Before any swing query or signal implementation, a new specification must define:

- hypothesis mechanism and identifier;
- data universe and timestamp cutoff;
- feature and label definitions;
- entry and exit rules;
- holding horizon;
- fees, spread, slippage, and funding treatment;
- discovery/OOS split;
- purge or embargo rule where labels overlap;
- minimum sample and pass/kill gate;
- independent verification owner.

Historical data expansion may be performed as infrastructure work, but the same frozen H-SW1 rule must not be retuned after observing outcomes. A larger dataset may justify rerunning the unchanged rule; changing the rule creates a new lineage.

## Next-agent instructions

The next writer must read this file, `AGENTS.md`, `docs/EXPERIMENT_LEDGER.md`, and `docs/SUPABASE_RECOVERY_RUNBOOK.md` before editing. Treat live database claims as unverified until supported by a Supabase export, query result, or deployment evidence. Keep trading disabled.
