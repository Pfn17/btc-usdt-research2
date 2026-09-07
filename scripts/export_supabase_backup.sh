#!/usr/bin/env bash
set -Eeuo pipefail

OUT_DIR="${1:-backups/supabase/$(date -u +%Y%m%dT%H%M%SZ)}"
DB_URL="${SUPABASE_DB_URL:-${DATABASE_URL:-}}"

if [[ -z "$DB_URL" ]]; then
  echo "SUPABASE_DB_URL or DATABASE_URL is required" >&2
  exit 2
fi

command -v pg_dump >/dev/null || { echo "pg_dump is required" >&2; exit 2; }
command -v psql >/dev/null || { echo "psql is required" >&2; exit 2; }

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

DUMP_ARGS=(--no-owner --no-privileges --schema=public --format=plain)

echo "Exporting public schema..."
pg_dump "$DB_URL" "${DUMP_ARGS[@]}" --schema-only > "$OUT_DIR/schema.sql"

echo "Exporting public data..."
pg_dump "$DB_URL" "${DUMP_ARGS[@]}" --data-only > "$OUT_DIR/data.sql"
cat "$OUT_DIR/schema.sql" "$OUT_DIR/data.sql" > "$OUT_DIR/full.sql"

echo "Exporting catalog inventory..."
psql "$DB_URL" -X -v ON_ERROR_STOP=1 -At -F $'\t' > "$OUT_DIR/catalog_inventory.tsv" <<'SQL'
SELECT 'table',n.nspname||'.'||c.relname,c.relkind,
       COALESCE((SELECT count(*)::text FROM pg_attribute a WHERE a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped),'0')
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','f')
UNION ALL
SELECT 'function',n.nspname||'.'||p.proname||'('||pg_get_function_identity_arguments(p.oid)||')',p.prokind,''
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE n.nspname='public'
UNION ALL
SELECT 'trigger',n.nspname||'.'||c.relname||'.'||t.tgname,'trigger',''
FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND NOT t.tgisinternal
UNION ALL
SELECT 'policy',n.nspname||'.'||c.relname||'.'||pol.polname,'policy',''
FROM pg_policy pol JOIN pg_class c ON c.oid=pol.polrelid JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public'
UNION ALL
SELECT 'extension',extname,extversion,'' FROM pg_extension
ORDER BY 1,2;
SQL

echo "Exporting pg_cron jobs..."
if ! psql "$DB_URL" -X -v ON_ERROR_STOP=1 -At -F $'\t' > "$OUT_DIR/cron_jobs.sql" <<'SQL'
SELECT format('-- jobid=%s schedule=%L active=%s database=%L username=%L command=%L',
              jobid, schedule, active, database, username, command)
FROM cron.job
ORDER BY jobid;
SQL
then
  echo "Unable to read cron.job; cron backup is incomplete" >&2
  exit 3
fi

{
  echo "backup_created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "project_ref=${SUPABASE_PROJECT_REF:-unknown}"
  echo "git_commit=$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "pg_dump=$(pg_dump --version)"
  echo "psql=$(psql --version)"
  echo "schema_bytes=$(wc -c < "$OUT_DIR/schema.sql")"
  echo "data_bytes=$(wc -c < "$OUT_DIR/data.sql")"
  echo "full_bytes=$(wc -c < "$OUT_DIR/full.sql")"
  echo "catalog_rows=$(wc -l < "$OUT_DIR/catalog_inventory.tsv")"
  echo "cron_rows=$(wc -l < "$OUT_DIR/cron_jobs.sql")"
} > "$OUT_DIR/BACKUP_METADATA.txt"

sha256sum "$OUT_DIR/schema.sql" "$OUT_DIR/data.sql" "$OUT_DIR/full.sql" \
  "$OUT_DIR/catalog_inventory.tsv" "$OUT_DIR/cron_jobs.sql" "$OUT_DIR/BACKUP_METADATA.txt" \
  > "$OUT_DIR/SHA256SUMS"

chmod 600 "$OUT_DIR"/*.sql "$OUT_DIR"/*.tsv "$OUT_DIR"/*.txt

echo "Backup written to $OUT_DIR"
