# Two-Method Verification Handoff — 2026-09-08

The owner requested two read-only verification methods to be implemented and displayed together.

## Method identities

| Method | API endpoint | RPC | Interpretation |
|---|---|---|---|
| `H-SW1-CLAUDE` | `/api/v1/research/sw1-claude` | `research_sw1_scan_frozen` | Official Claude method reported as already live and verified in Supabase; still requires independent evidence review by Manus |
| `H-SW1-MANUS` | `/api/v1/research/sw1-manus` | `research_sw1_manus_scan_frozen` | Independent Manus implementation; not interchangeable with the official method |

The Manus SQL migration was renamed so it cannot overload or silently replace the official Claude function. The dashboard labels both methods explicitly.

## Why the names are separate

Claude's audit identified three material differences between the supplied Manus SQL and the live official function: candidate grid construction, average-sign versus unanimous-sign funding agreement, and NTILE quartile grouping versus calendar quarters. These differences define separate methodological lineages even though both are 24-hour swing-lite research.

## Safety and verification boundary

Both endpoints are read-only, return `trading_enabled: false`, and are displayed as research evidence rather than trading approval. No live RPC result was fabricated by this writer. If either RPC is unavailable, the dashboard displays an unavailable state.

The official Claude function must be verified with its live output, exact cutoff, and backup evidence. The Manus function must be applied separately and compared only as an independent method. Neither result should be promoted to paper or live execution based on a positive point estimate alone.
