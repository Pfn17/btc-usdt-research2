# HyperHan Lab Dashboard Architecture

HyperHan Lab is one read-only research archive presented as one continuous mobile-first page. The page is ordered **Story → Terminal → Visual**. The sections are always present in the document and are reached by vertical scrolling or anchor navigation; no research evidence is hidden behind a tab switch.

## Page sections

| Order | Section | Owner purpose | Evidence surface | Refresh policy |
|---|---|---|---|---:|
| 1 | **Story** | Landing context, owner identity, project background, collaboration context, and evidence boundary | Backend-derived health, audit count, and current market fact; narrative context is visibly separated from live facts | 15 minutes |
| 2 | **Terminal** | Primary research and operational archive | Current BTCUSDT state, collector health, funding observation, safety gate, H-FB1 decision, H-SW1 persisted comparison, research status, and system health | 15 seconds for operational reads |
| 3 | **Visual** | Visual explanation of existing evidence | Labelled OHLCV chart, observation window, EV/CI95 whisker view, and static evidence-path map | 15 minutes |

## Resource boundaries

The dashboard uses `loadOperational()` for current health, market, funding, audit, and governance-summary reads, and `loadResearch()` for the frozen H-FB1/H-SW1 result reads. The operational loop runs every 15 seconds; research refreshes every 15 minutes and is also loaded once at startup. This keeps the initial page complete without repeatedly spending research RPC capacity on an operational cadence. All reads remain read-only and create no new scan or database write.

The OHLCV chart uses the production-safe limit of 20 records. Its SVG includes maximum, midpoint, and minimum price labels, plus first and last candle timestamps. The EV/CI95 whisker chart renders only returned research fields. Missing fields remain `UNAVAILABLE`; no estimate is inferred from another result.

The evidence-path diagram uses neutral terms: **Market observations → Collection → Research record → Owner view**. It does not claim a vendor, host, database, API path, or RPC name in the owner-facing surface.

## Design rules

The priority order is **values and integrity, information architecture, clarity, professional restraint, then aesthetics**. The dashboard must not use mock data, dummy data, fabricated live numbers, disguised errors, unsupported performance claims, hidden execution, gradients, glassmorphism, pulsing decorative dots, or AI/model branding.

CSS is mobile-first. The base layout is one column. Wider grids are introduced only at `min-width: 768px`. SVG elements use responsive width, automatic height, and a preserved aspect ratio so the evidence remains readable on narrow screens.

## Owner identity and failure behavior

The public owner identity is **@parhanfirdausnugraha**. It appears in the header. The footer identifies the archive as read-only, states that trading execution is disabled, and states that there is no validated edge. The owner-facing memory section reads the latest active owner decision and approved recommendation from the governance summary endpoint; it does not expose the full governance tables.

If a live request fails, the affected field or resource reports its actual unavailable state. The page does not downgrade honesty to preserve visual completeness. This behavior is part of the research audit trail.
