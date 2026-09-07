# Backup policy and live dashboard contract

The project preserves research knowledge, configuration, conclusions, and provenance in Git while treating refetchable raw market/funding data as external inputs. Significant batches must produce a commit with experiment lineage, frozen parameters, costs, cutoff/dataset identity, result status, evidence, and next action. Database behavior changes must include migration/function/policy/trigger/cron definitions or a verified reference to them.

The dashboard is **backend-only and live-only**: never placeholder, dummy, mock, fabricated, or guessed data. Missing or stale backend values must render as an explicit unavailable/degraded state with reason and timestamp. Trading remains disabled until a separately approved execution phase is recorded in the ledger.

See `research-vault/` for the durable policy and the 2026-09-07 Supabase audit snapshot.
