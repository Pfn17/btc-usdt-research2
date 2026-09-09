# Dashboard Pages

The dashboard is one application with three real pages, not three skins. The page navigation changes the information architecture and the purpose of the view.

| Page | Owner purpose | Content | Refresh |
|---|---|---|---|
| Overview | Primary monitoring surface | Current BTCUSDT price, funding observation, freshness, safety gate, decision state, and system health | 15 seconds |
| Visual | Mobile-native alternative analytical view | Backend-derived close chart, observation window, lightweight metrics, evidence-path map, and manually requested frozen-study comparison | 5 minutes; comparison is manual |
| Story | Public portfolio, background, collaboration, and pitching context | Project narrative plus live proof points such as current price, health, and captured audit count | 5 minutes |

Overview is the only page intended for continuous monitoring. Visual and Story deliberately use a slower cadence because they are alternative perspectives, not operational streams. Visual uses a light, mobile-first card hierarchy, safe-area bottom navigation, rounded sheet surfaces, and a segmented page control; these are structural interaction choices, not merely a recoloring of Overview.

All values are sourced from the existing backend API. Visual uses an inline SVG chart computed in the browser from the existing 24-candle OHLCV response; it adds no library, endpoint, storage, or database write. Story combines persisted project context with backend-derived facts and explicitly states the evidence boundary. If the API is unavailable, the page shows an unavailable state rather than inventing values.

The page choice is stored locally in the browser and does not alter research parameters, execution state, or data queries beyond the page-specific read set. No page promotes a method or claims a validated edge.
