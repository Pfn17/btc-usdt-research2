# HyperHan Lab Dashboard Architecture

HyperHan Lab is one read-only research archive presented as one continuous mobile-first page. The page is ordered **Current position → Research → Evidence → System**. The sections are reached by vertical scrolling; research evidence is not hidden behind a management or governance view.

## Page sections

| Order | Section | Purpose | Evidence surface | Refresh policy |
|---|---|---|---|---:|
| 1 | **Current position** | State the current research conclusion and safety boundary | Frozen decision summary and execution state | Static copy plus backend refresh |
| 2 | **Research** | Show frozen research measurements and separate H-SW1 lineages | H-FB1, H-SW1 reference/Claude, H-SW1 independent/Manus, N, net EV, CI95, and decision | Research refresh every 15 minutes |
| 3 | **Evidence** | Show current observations and decision-boundary visualization | OHLCV chart, observation window, EV/CI95 view, and neutral evidence path | Operational data every 15 seconds; derived research view every 15 minutes |
| 4 | **System** | Show whether the archive can currently observe and report data | Health, collector, market/funding freshness, event count, provenance, verification, and execution | Operational refresh every 15 seconds |

## Resource boundaries

The dashboard uses `loadOperational()` for health, market, funding, audit, and verification reads, and `loadResearch()` for the frozen H-FB1/H-SW1 result reads. Operational data refreshes every 15 seconds; research refreshes every 15 minutes and once at startup. All reads are read-only and create no new scan or database write. Governance records remain durable in Supabase and are intentionally kept outside the research presentation.

The OHLCV chart uses the production-safe limit of 20 records. Its SVG includes maximum, midpoint, and minimum price labels, plus first and last candle timestamps. The EV/CI95 view renders only returned research fields. Missing fields remain `UNAVAILABLE`; no estimate is inferred from another result.

The evidence path uses neutral terms: **Market observations → Collection → Research record → Research archive**. It does not claim a vendor, host, database, API path, or RPC name. H-SW1 lineage names are shown only where needed to distinguish the two materially different frozen methods.

## Design rules

The priority order is **values and integrity, information architecture, clarity, professional restraint, then aesthetics**. The dashboard must not use mock data, fabricated live numbers, disguised errors, unsupported performance claims, hidden execution, gradients, glassmorphism, pulsing decorative dots, or AI/model branding.

CSS is mobile-first. The base layout is one column. Wider grids are introduced only at `min-width: 768px`. SVG elements use responsive width, automatic height, and a preserved aspect ratio so the evidence remains readable on narrow screens.

## Failure behavior

If a live request fails, the affected field or resource reports its actual unavailable state. The page distinguishes loading, ready, stale, and unavailable states. It does not downgrade honesty to preserve visual completeness.
