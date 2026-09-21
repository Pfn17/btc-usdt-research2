# Executable PnL Contract — v1.1

Status: FROZEN / GATE 0 — 2026-09-22

The purpose of this contract is to decide whether a research observation may be called EXECUTABLE PnL. A positive forward-return proxy is not sufficient.

## Result classes

1. EXECUTABLE_PNL — decision-time information, entry/fill, exit/fill, latency, costs, and applicable funding cashflow are reconstructible.
2. FORWARD_RETURN_PROXY — the result measures a future price change but one or more executable fill semantics are not reconstructible.
3. UNVERIFIABLE — a required timestamp, price, cost, or provenance component is missing or contradictory.

Only EXECUTABLE_PNL may support a profit/promotion claim.

## Required trade invariant

Each executable observation must expose:

- decision_timestamp
- signal_timestamp
- information-availability state at decision time
- entry_available_timestamp
- entry_price
- exit_timestamp
- exit_price
- latency assumption actually applied
- fee per side
- slippage per side
- funding cashflow when applicable
- overlap state/rule
- valid / invalid
- invalid reason when invalid
- dataset cutoff
- implementation identity

Missing required evidence must never silently become an executable trade.

## Time semantics

Signal-time, fill-time, and evaluation-time are separate:

- Signal-time: when the frozen signal becomes knowable.
- Fill-time: when the position is assumed executable and at which price.
- Evaluation-time: when the position is closed or valued.

No signal may use a price or feature that becomes available after signal-time.

## Universal return formulas

LONG:

gross_bps = (exit / entry - 1) × 10,000

SHORT:

gross_bps = (entry / exit - 1) × 10,000

Then:

net_bps = gross_bps - fee - slippage - other_declared_costs

Baseline remains 4 bps fee per side + 1 bps slippage per side = 10 bps round trip. Stress remains 12 bps round trip.

Gross, baseline net, stress net, and forward-return proxy values must never be displayed as interchangeable metrics.

## Execution rules

1. Decision time — only information available at or before decision-time is eligible.
2. Entry — the fill rule must be explicitly frozen. Next-bar/open is acceptable where preregistered; an unstated close-to-close return is not executable PnL.
3. Exit — timestamp and executable fill rule must be explicit. If the required price is unavailable, invalidate rather than bridge.
4. Latency — modeled latency must shift the fill timestamp/price. Zero latency is valid only if explicitly frozen.
5. Funding — include funding cashflow whenever the position crosses a funding event.
6. Overlap — non-overlap is the default unless another rule was frozen before OOS.
7. Missing data — affected windows are invalid. No interpolation, nearest-row substitution, or silent timestamp bridging.
8. Provenance — implementation identity and dataset cutoff must be replayable.

## Gate 0 decisions

- PASS — contract and implementation replay as executable PnL.
- PASS WITH PROXY LIMITATION — statistics replay, but the historical result cannot satisfy the executable-PnL invariant. It must be labeled FORWARD_RETURN_PROXY.
- BLOCKED — required implementation, provenance, timestamp, fill, or cost evidence cannot be reconciled.

Gate 0 is a permission gate. PASS WITH PROXY LIMITATION cannot enter a profit promotion path.

## Historical audit matrix — 2026-09-22

| Result | Entry / exit | Latency | Costs | Funding | Missing / overlap | Economic class | Gate 0 |
|---|---|---|---|---|---|---|---|
| H-FB3 | Frozen next 1m open / fifth held 1m close documented | One-candle boundary documented | 10 / 12 bps frozen | Not part of mechanism | Exact non-overlap documented; dataset has audited gaps | Needs implementation-level replay | BLOCKED pending source replay |
| H-MR1 | Next available open; exit allowed within a 1h–2h timestamp window in implementation | Not an explicit fill-latency model | 10 / 12 bps | Not applicable | Row-based 15m lag and tolerant exit can alter elapsed-time semantics | FORWARD_RETURN_PROXY | PASS WITH PROXY LIMITATION |
| H-BASIS1 | Historical implementation uses mark-price proxy, not independently frozen exchange fill | Entry delay is 1 minute in historical analysis | 10 / 12 bps | Not modeled as funding cashflow | Historical non-overlap; raw extract replayable | FORWARD_RETURN_PROXY | PASS WITH PROXY LIMITATION |
| H-VOL1 | Frozen next 1m open / exact 120m elapsed exit | One-candle delay documented | 10 / 12 bps | Not applicable | Exact timestamps required; outcome not run | UNRUN | BLOCKED / NOT YET AUTHORIZED |
| H-FB1 / Funding-sign | Historical forward/funding-event statistics exist, but project-wide executable invariant was not captured | Not sufficient for current invariant | Historical 10 bps convention | Funding semantics vary | Historical provenance requires separate replay | UNVERIFIABLE / PROXY | BLOCKED |
| H-FB2 | Funding-event mark-price entry documented | Execution fill not independently captured | 10 bps documented | Funding cashflow included in frozen rule | Historical result exists; current Gate 0 replay not yet performed | FORWARD_RETURN_PROXY until replay | BLOCKED pending source replay |
| 4H Momentum | Historical return statistic; executable entry/exit evidence not fully reconciled | Not fully evidenced | 10 bps historical convention | Not applicable | Not fully reconciled | UNVERIFIABLE | BLOCKED |
| H-SW1 | Multiple historical signatures/methods | Not fully reconciled | Cost-adjusted result exists | Funding agreement logic varies | Provenance identity must be selected before executable claim | UNVERIFIABLE | BLOCKED |

## Interpretation

This matrix does not change any historical economic result. It changes only the label that may be attached to that result under Gate 0.

H-MR1 and H-BASIS1 remain historical research evidence, but their existing implementations do not satisfy the new executable-PnL invariant. Their economics must therefore not be described as proven live-trading PnL.

## Synthetic economics gate

The deterministic Gate 0 harness must test:

- LONG positive return formula;
- SHORT positive return formula;
- 10 bps cost killing an 8 bps gross edge;
- latency moving the fill away from signal-time;
- missing exit invalidating the observation;
- overlap suppression under the frozen rule;
- funding cashflow changing net PnL;
- post-decision price/information being rejected.

These tests validate the contract only. They are not market-edge evidence.

## Promotion boundary

A future candidate may enter promotion only when:

- class = EXECUTABLE_PNL;
- net EV > 0 after 10 bps baseline;
- CI95 lower bound > 0;
- 12 bps stress remains positive;
- independent calendar/regime coverage passes the preregistered minimum;
- LONG and SHORT behavior does not hide a failed side;
- deterministic replay matches;
- no parameter changes occurred after OOS observation.

Trading authorization remains OFF.

## Stop condition

If the Gate 0 synthetic economics harness or representative historical replay cannot satisfy the invariant, do not start new data capture or hypothesis discovery. Fix the contract/replay layer first.
