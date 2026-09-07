# Supabase audit backup (read-only)

Generated 2026-09-07 for project `btc-usdt-research2` (`xaqsntunrqvqpzlbeutt`).

This package is an **audit artifact**, not a complete `pg_dump` restore. It contains the live function definitions, the 41-row coordination ledger, the Edge Function source, and a manifest of objects observed during the audit. No external mutation was performed.

## Important limitations

The repository `Pfn17/btc-usdt-research` was empty at audit time. The large market-data tables were not copied into Git. Supabase internal schemas (`auth`, `storage`, `vault`, and `realtime`) were intentionally excluded because they may contain credentials, identities, or platform-managed data. The migration list was inspected but migration file bodies were not retrievable through the configured read-only tools in this audit.

Before relying on this as a disaster-recovery backup, obtain a full schema-and-data dump through an approved Supabase/Postgres backup path, store secrets in a secret manager, and test restoration into a disposable project.

## Files

- `manifest.json` — provenance, counts, and exclusions.
- `functions.json` — definitions returned by `pg_get_functiondef` for public functions; extension-owned HTTP functions are included as observed.
- `agent_coordination_log.json` — all 41 ledger rows, exported with fields only; no secrets were added.
- `edge_function_debug-hfb1-probe.ts` — source returned by Supabase for the single active Edge Function.

## Security review findings

Supabase advisory output reported RLS-enabled tables without policies, mutable search paths on several research functions, HTTP extension in `public`, and publicly executable `SECURITY DEFINER` functions. These findings were recorded, not remediated, because this task was explicitly read-only.
