# Dashboard Modes

The dashboard provides three local presentation modes over the same backend responses. The selector changes layout and visual treatment only; it never changes a query, research parameter, result, or execution state.

| Mode | Purpose | Additional content |
|---|---|---|
| Terminal | Default market archive for quick monitoring | Compact cards, health state, audit log, and frozen research summaries |
| Clean | Calm reading console | Recent-close SVG chart computed from the existing OHLCV response |
| Story | Portfolio and research narrative | The same chart plus observed candle count, window, close change, and explanatory context |

The chart is deliberately lightweight. It is an inline SVG generated in the browser from the existing 24-candle OHLCV response. It uses no chart library, no new endpoint, no database write, and no external asset. If the backend response contains insufficient data, the chart remains unavailable rather than fabricating a line.

The mode choice is stored only in browser `localStorage`. It is not a user account setting and does not affect other viewers. The default is Terminal.
