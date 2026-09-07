# Backup policy and live dashboard contract

The project preserves research knowledge, configuration, conclusions, and provenance in Git while treating refetchable raw market/funding data as external inputs. Significant batches must produce a commit with experiment lineage, frozen parameters, costs, cutoff/dataset identity, result status, evidence, and next action. Database behavior changes must include migration/function/policy/trigger/cron definitions or a verified reference to them.

The owner requires all services to remain on free tiers until the project has generated paid revenue. No agent may purchase or activate a paid plan without explicit owner approval. Free-tier capacity is enforced through bounded data windows, retention, no duplicate collectors, no high-frequency AI schedules, and measured usage before backfills or deployments. See `docs/FREE_TIER_GOVERNANCE.md` for the restore and capacity rules.

The dashboard is **backend-only and live-only**: never placeholder, dummy, mock, fabricated, or guessed data. Missing or stale backend values must render as an explicit unavailable/degraded state with reason and timestamp. Trading remains disabled until a separately approved execution phase is recorded in the ledger.

See `research-vault/` for the durable policy and the 2026-09-07 Supabase audit snapshot.

At the beginning of each session, check the latest `main` commit and coordination ledger. After each significant batch, commit and push the durable artifacts before starting the next batch. A periodic raw-data backup is not required; raw data remains refetchable and should not consume Git or provider capacity unnecessarily.
