# HyperHan Lab Dashboard Architecture

HyperHan Lab is one read-only research archive presented as one continuous mobile-first page. The page is ordered **Story → Terminal → Visual**. The sections are always present in the document and are reached by vertical scrolling or anchor navigation; no research evidence is hidden behind a tab switch.

## Page sections

| Order | Section | Owner purpose | Evidence surface | Refresh policy |
|---|---|---|---|---:|
| 1 | **Story** | Landing context, owner identity, project background, collaboration context, and evidence boundary | Backend-derived health, audit count, and current market fact; narrative context is visibly separated from live facts | 15 minutes |
| 2 | **Terminal** | Primary research and operational archive | Current BTCUSDT state, collector health, funding observation, safety gate, H-FB1 decision, H-SW1 persisted comparison, research status, and system health | 15 seconds for operational reads |
| 3 | **Visual** | Visual explanation of existing evidence | Labelled OHLCV chart, observation window, EV/CI95 whisker view, and static evidence-path map | 15 minutes |

## Resource boundaries

The existing `loadStory()`, `loadTerminal()`, and `loadVisual()` functions remain the backend read boundary. Terminal runs on a fast operational loop. Story and Visual run on one slow 15-minute loop. Frozen research comparison is read-only and uses the already defined research endpoints; it does not create a new scan or database write.

The OHLCV chart uses the production-safe limit of 20 records. Its SVG includes maximum, midpoint, and minimum price labels, plus first and last candle timestamps. The EV/CI95 whisker chart renders only returned research fields. Missing fields remain `UNAVAILABLE`; no estimate is inferred from another result.

The evidence-path diagram uses the neutral term **Collector runtime**. It does not claim Railway or any other host unless that hosting fact is independently verified in the backend or deployment evidence.

## Design rules

The priority order is **values and integrity, information architecture, clarity, professional restraint, then aesthetics**. The dashboard must not use mock data, dummy data, fabricated live numbers, disguised errors, unsupported performance claims, hidden execution, gradients, glassmorphism, pulsing decorative dots, or AI/model branding.

CSS is mobile-first. The base layout is one column. Wider grids are introduced only at `min-width: 768px`. SVG elements use responsive width, automatic height, and a preserved aspect ratio so the evidence remains readable on narrow screens.

## Owner identity and failure behavior

The public owner identity is **@parhanfirdausnugraha**. It appears in the header and footer. The footer identifies the archive as read-only, states that trading execution is disabled, and states that there is no validated edge.

If a live request fails, the affected field or resource reports its actual unavailable state. The page does not downgrade honesty to preserve visual completeness. This behavior is part of the research audit trail.
