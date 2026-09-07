# HyperHan Lab Research Vault

This directory is the durable, reviewable source of truth for research knowledge and reproducibility. Raw market, funding, order-book, and feature data remain in Supabase or are refetched from their upstream source; the vault preserves what cannot safely be reconstructed from raw data alone.

## Persist in Git

Commit hypotheses, preregistrations, experiment lineage, frozen parameters, cutoff timestamps, dataset hashes, cost models, walk-forward/purge/embargo rules, research results and their status, rejected/inconclusive findings, Supabase migrations/functions/policies/triggers/cron definitions, redacted deployment configuration, coordination snapshots, decisions, and verification evidence.

## Never commit

Never commit API keys, service-role keys, exchange credentials, JWT secrets, passwords, `.env` files, or raw high-volume market data. Use `.env.example` files with variable names only. Review `git diff --cached` and run secret scanning before every push.

## Batch rule

Create a backup commit after each significant research or infrastructure batch. A batch is significant when it changes a hypothesis, experiment rule, cost model, schema/function/policy/cron, dashboard data contract, deployment behavior, or a conclusion. Every batch must record its rationale, evidence, status, and next action.

## Restore rule

A snapshot is not considered restorable until it has been tested in a disposable Supabase project. The `backups/supabase/*` artifacts are provenance snapshots; a full `pg_dump` remains the preferred recovery path when database credentials are available.
