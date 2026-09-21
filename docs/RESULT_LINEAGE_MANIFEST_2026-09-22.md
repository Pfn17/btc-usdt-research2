# Result lineage manifest — 2026-09-22

This manifest records the canonical implementation selected for representative historical results and the independent replay outcome.

| Hypothesis | Result | Canonical implementation | Replay | Status |
|---|---|---|---|---|
| H-MR1 | 7d34c319-f9b0-4762-99af-3b050d8975c8 | `research_hmr1_scan_frozen_v2(bigint,bigint,numeric,numeric,numeric)` | Exact frozen replay: n=190, net=-3.0303795 bps, stress=-5.0303795 bps, CI matches | MATCH |
| H-BASIS1 | 907bf0bb-9ed5-4456-94ce-cf8dda2b5e26 | `research_funding_basis_scan_frozen(bigint,integer,integer,numeric,numeric)` | Current RPC returns n=7,412 / 2,862 by agreement, not historical n=156 | MISMATCH |

## Interpretation

H-MR1 has a reproducible canonical lineage for the representative killed result.

H-BASIS1 does not. The current live RPC cannot reproduce the historical persisted result. The historical implementation must therefore be recovered from the exact source/migration lineage before that result can be treated as fully reproducible.

This is a provenance finding, not a claim that the historical H-BASIS1 result was fabricated or that the current RPC is wrong. It means the project currently lacks a deterministic bridge between the historical result and the implementation that generated it.

Trading remains OFF. No hypothesis is reopened from this finding.
