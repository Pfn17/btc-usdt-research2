# Backup and provenance policy

The Git repository is the source of truth for research logic, configuration, decisions, and reproducibility metadata. Supabase is the source of truth for live data and coordination state. Raw market/funding data may be refetched and is not required in Git when its source, time range, schema, and checksum/provenance are recorded.

Every significant batch produces a commit containing:

1. the exact changed files;
2. a redacted configuration snapshot;
3. migration/function/policy/trigger/cron definitions if database behavior changed;
4. experiment identifiers, frozen parameters, cutoff, dataset hash, cost model, and result status;
5. evidence and next action;
6. the current coordination-ledger snapshot or a ledger reference.

A commit is not proof of deployment or database application. Deployment/runtime and database verification must be recorded separately with an identifiable SHA, migration version, query result, or deployment ID.
