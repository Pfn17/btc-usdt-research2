# Cross-System Sync Checkpoint — 2026-09-09

**Writer:** Manus 1  
**Repository:** `Pfn17/btc-usdt-research2`  
**Canonical branch:** `main`  
**Head after this checkpoint:** `5b51f8121340cad5dae08194e38b24dd23b36984`

## Canonical state

GitHub `main`, the production Supabase migration history, and the experiment ledger are synchronized for the current H-SW1 and dashboard work.

| Area | Canonical state | Evidence |
|---|---|---|
| Dashboard | Three real pages: Overview, Visual, Story; Overview refreshes at 15s, the other pages at 5m | commit `5b51f81` |
| H-SW1 reference | Claude lineage, text-typed RPC | `research_sw1_scan_frozen(text,numeric,numeric,integer)` |
| H-SW1 independent | Manus lineage, bigint-typed RPC | `research_sw1_manus_scan_frozen(bigint,numeric,numeric,integer)` |
| Manus migration | Applied in Supabase | migration `20260908025302` / `20260908_hsw1_manus_swing_lite` |
| Live result interpretation | Both methods INCONCLUSIVE / NOT PROMOTED | `docs/HSW1_LIVE_VERIFICATION_2026-09-09.md` |
| H-FB1 | KILL | `docs/EXPERIMENT_LEDGER.md` |
| Funding family | CLOSED | `docs/EXPERIMENT_LEDGER.md` |
| Execution | OFF | dashboard safety gate and ledger |

## Supabase migration inventory relevant to current work

The live migration list includes both swing registration/freeze migrations and the applied Manus migration:

- `20260907031459_register_h_sw1_swing_family`
- `20260907031535_register_h_sw1_swing_family_fix`
- `20260908013128_add_swing_lite_frozen_scan`
- `20260908025302_20260908_hsw1_manus_swing_lite`

No new DDL was applied during this synchronization checkpoint.

## Coordination-log context

Some older coordination rows remain as historical proposals or blocking findings. They are not deleted because they are audit evidence. Their interpretation is:

- `hsw1-migration-signature-collision-2026-09-08`: historical blocking finding; resolved by preserving the Claude signature and applying Manus under a distinct function name.
- `hsw1-manus-rpc-apply-2026-09-08`: implementation claim; live migration and function signatures are now verified.
- `dashboard-3mode-architecture-spec-2026-09-08`: historical design proposal; implemented by commit `689dcd4`.
- `dashboard-3mode-mode3-chart-svg-2026-09-08`: historical component proposal; Story / Visual now contains a live-price chart and EV/CI chart using cached backend data.
- `dashboard-themes-phase2-boundary-2026-09-08`: historical draft wording; superseded by page-level information architecture. Overview is the owner monitoring surface; Visual is a slower analytical view; Story is the public portfolio/background view. Phase 2 remains unrun.

Historical rows remain visible intentionally; none should be interpreted as an active unowned task without checking this checkpoint and the current Git head.

## Open pull requests

PRs #1, #2, and #3 remain open on a separate, older Futures L2 collector branch chain from 2026-08-28. They are not part of the current H-SW1/dashboard implementation and were not closed automatically. They require an explicit owner decision: merge, close as superseded, or retain for future L2 work. This checkpoint records that distinction so they are not mistaken for missing dashboard work.

## Safety boundary

This checkpoint changes documentation only. It does not promote any method, run a new research scan, alter a frozen result, enable paper/live orders, close pull requests, or delete coordination history.
