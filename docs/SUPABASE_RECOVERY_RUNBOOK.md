# Supabase Recovery Runbook

**Project:** `btc-usdt-research2`  
**Supabase project ref:** `xaqsntunrqvqpzlbeutt`  
**Purpose:** preserve the research system if the current Supabase project becomes unavailable or must be recreated.

## Executive conclusion

The repository already contains five versioned migrations, but the repository is **not yet a complete backup of the live Supabase project**. A migration history is not equivalent to a database backup because it does not contain live rows, coordination history, manually-created objects, cron configuration, or changes applied outside the migration directory.

The two files supplied for this audit are not database dumps. One contains a proposed backfill implementation and the other contains an audit narrative. They cannot be used to restore Supabase.

The authoritative recovery artifact must contain both:

1. a logical PostgreSQL dump of schema and data; and
2. a separate export of Supabase-specific operational metadata that is not guaranteed to be included by `pg_dump`, especially scheduled jobs.

## Current audit status — 2026-09-07

| Asset | Current evidence | Recovery status |
|---|---|---|
| Repository migrations | Five SQL migrations under `supabase/migrations/` | Versioned in Git |
| Research documentation | `docs/EXPERIMENT_LEDGER.md`, protocol, state, and audit documents | Versioned in Git |
| Coordination log | Claude report claims 41 rows, but no SQL/JSON export was attached | **Not independently archived** |
| Live table data | No complete PostgreSQL dump was attached | **Not independently archived** |
| Manual functions, policies, triggers | Not independently compared with `pg_catalog` | **Unverified** |
| `pg_cron` jobs | Not independently exported | **Unverified** |
| Public REST check | `agent_coordination_log` returned `HTTP 200 []` with the publishable key | Does not prove the table is empty; RLS or public visibility may hide rows |

Do not mark the backup complete until every item marked **not archived** or **unverified** has evidence in a committed artifact.

## Required source credentials

Use a temporary database connection string with a password supplied through the shell environment. Do not place the password in Git, command history, issue comments, dashboard code, or this document.

```bash
export SUPABASE_DB_URL='postgresql://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres?sslmode=require'
```

The publishable Supabase key is not sufficient for a complete backup. It is intended for client-side access and cannot reliably export private tables, functions, policies, or database metadata.

## Create a logical backup

The repository includes `scripts/export_supabase_backup.sh`. Run it from the repository root:

```bash
./scripts/export_supabase_backup.sh
```

To choose an explicit destination:

```bash
./scripts/export_supabase_backup.sh backups/supabase/2026-09-07
```

The script creates:

| File | Contents |
|---|---|
| `schema.sql` | Public schema, tables, indexes, constraints, functions, triggers, policies, and grants supported by `pg_dump` |
| `data.sql` | Table data and sequences for the public schema |
| `full.sql` | Combined logical dump for one-step restoration |
| `cron_jobs.sql` | Explicit `pg_cron` job definitions when the connection can read `cron.job` |
| `catalog_inventory.tsv` | Inventory of tables, functions, triggers, policies, and extensions |
| `SHA256SUMS` | Checksums for the generated artifacts |
| `BACKUP_METADATA.txt` | Timestamp, project reference, and tool versions |

The generated directory is intentionally not committed automatically. Review its size and content first. A large OHLCV or feature dataset may exceed practical Git limits; in that case, store the dump in an encrypted object store and commit its immutable URL, checksum, creation timestamp, and restore instructions. Git should still contain the migrations and the recovery manifest.

## Verify a backup before committing or storing it

Run the following checks:

```bash
sha256sum -c backups/supabase/<DATE>/SHA256SUMS
wc -c backups/supabase/<DATE>/*.sql
rg -n "agent_coordination_log|CREATE FUNCTION|CREATE POLICY|CREATE TRIGGER|cron" backups/supabase/<DATE>
```

The coordination log must be checked separately because a public REST query returning an empty array is not evidence that the private table is empty. The backup must contain the expected row count and a readable sample after export.

## Restore into a new Supabase project

Restore only into a new or empty project after reviewing the target project reference and credentials.

```bash
psql "$NEW_SUPABASE_DB_URL" \
  --set ON_ERROR_STOP=on \
  --file backups/supabase/<DATE>/full.sql

psql "$NEW_SUPABASE_DB_URL" \
  --set ON_ERROR_STOP=on \
  --file backups/supabase/<DATE>/cron_jobs.sql
```

If the dump contains objects owned by the old project role, use the dump generated with `--no-owner --no-privileges` and re-apply intended grants from the migration files. Recreate secrets, connector configuration, Railway variables, and Vercel variables separately; they are not database rows and must never be included in a Git dump.

## Post-restore verification

A restore is not complete until the following checks pass:

1. All expected public tables exist.
2. The coordination log row count and a deterministic checksum match the backup manifest.
3. All research functions can be called with their recorded signatures.
4. RLS is enabled on every table that was protected in the source project.
5. Public read policies exist only where intended.
6. Triggers and indexes exist.
7. Cron jobs exist with the same schedule and command.
8. The application health endpoint works against the new project.
9. The collector can write one idempotent test event without creating a duplicate.
10. The dashboard displays real data or an explicit unavailable state.
11. Trading remains disabled.

## Retention and operating policy

A single end-of-period dump is insufficient. During the free-tier window, create at least one full dump immediately and repeat it after every material database change. Keep at least two independently verified copies in separate locations. Record each dump's timestamp, project reference, row counts, SHA-256 checksum, and storage location in Git.

Do not delete the current Supabase account merely because a replacement account is planned. Deletion is irreversible and should occur only after a successful restore rehearsal and independent verification of the new deployment.

## Research integrity boundary

A backup preserves evidence; it does not change research conclusions. H-FB1 and H-FB2 remain frozen according to the experiment ledger. A future swing-trading family must receive a new hypothesis identifier, frozen specification, cost model, OOS split, and acceptance gate. Restoring historical data must not be used to silently retune an existing experiment.

## References

[1]: https://supabase.com/docs/guides/database/backup-restore/backup-db "Supabase database backup and restore documentation"
[2]: https://www.postgresql.org/docs/current/app-pgdump.html "PostgreSQL pg_dump documentation"
[3]: https://supabase.com/docs/guides/database/extensions/pg_cron "Supabase pg_cron documentation"
