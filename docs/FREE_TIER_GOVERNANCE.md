# Free-Tier Governance

## Hard owner principle

**No paid plan is purchased until the project has generated paid revenue first.** This applies to every service used by the project: GitHub, Manus, Vercel, Railway, Supabase, Claude, ChatGPT, Grok, and future providers. The default operating assumption is that every service remains on its free tier indefinitely.

No agent may recommend or activate an upgrade, paid add-on, reserved hosting, billing change, or paid API plan without explicit owner approval after presenting the exact cost and reason.

## What this means technically

Free-tier capacity is a hard research constraint, not an inconvenience. The system must prefer low-frequency, batch-oriented, refetchable workflows over continuous polling and duplicate storage.

- Raw OHLCV, funding, order-book, and feature data are refetchable inputs. Do not duplicate them in Git.
- Persist research knowledge, hypotheses, frozen configurations, results, decisions, migrations, and provenance in Git.
- Use the smallest sufficient data window and record the cutoff, source, row count, and dataset hash.
- Keep retention policies on high-volume tables and check database size before and after any backfill.
- Do not run minute-level or hour-level AI schedules for deterministic checks. They consume scarce execution quota without adding judgment.
- Do not run duplicate collectors, overlapping backfills, repeated research scans, or retuning loops.
- A dashboard refresh is not permission to create a new database write or research run.
- Research functions must be explicitly frozen and called once per preregistered batch unless the ledger authorizes a new lineage.
- Trading execution remains disabled.

## Backup cadence

A backup commit is required after each significant batch, including a change to a hypothesis, experiment rule, cost model, database behavior, dashboard data contract, deployment behavior, or research conclusion. The commit must include the exact changed files and a ledger reference.

A daily or hourly backup scheduler is **not** required for raw data and would consume free-tier capacity. The durable rule is event-driven: commit immediately after a significant batch, before starting the next batch. At the start of every Manus session, check GitHub `main`, the coordination ledger, and the latest backup commit. If a significant local change exists, stop and create the backup commit before doing more work.

## Capacity guardrails

Before a data or infrastructure operation, record:

1. current service and database usage;
2. expected additional rows/bytes/requests;
3. retention and rollback plan;
4. the owner-approved limit;
5. the ledger task ID.

Abort when the operation would threaten the provider's free-tier cap, when usage cannot be measured, or when a free-tier limit is approaching without a documented fallback. Never claim that a provider can "never" hit a limit; only measured budgets and bounded operations can reduce that risk.

## Account reset / restore

If a service account expires or is replaced, restore in this order:

1. clone `Pfn17/btc-usdt-research2`;
2. read `AGENTS.md`, this policy, the research protocol, and the latest handoff;
3. recreate the new free-tier projects;
4. apply versioned migrations and functions;
5. restore coordination and research metadata from `research-vault/`;
6. refetch only the raw data windows required by active experiments;
7. verify dashboard endpoints with real backend responses;
8. record new project IDs, deployment IDs, and verification evidence in the ledger.

Secrets are recreated manually or through the provider's secret manager. They are never restored from Git.

## Current approved operating mode

All services remain free-tier. No paid plan or billing change is approved. Work is limited to read-only research, bounded ingestion, versioned backup, and dashboard observability until the owner approves a separate execution phase.
