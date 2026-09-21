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

## Historical audit matrix — Gate 0.5 — 2026-09-22

| Result | Required economic evidence | Replay / lineage | Classification | Gate 0.5 |
|---|---|---|---|---|
| H-MR1 | Next-1m-open entry exists, but exit is first available close in a 60–120 minute timestamp window; latency is not an explicit market-latency model | Canonical v2 replay exact: N=190 and stored metrics match | FORWARD_RETURN_PROXY / PROXY_REPLAY_MATCH | PASS WITH PROXY LIMITATION |
| H-VOL1 | Next-1m-open entry and exact +120m open-time exit; 10/12 bps costs; deterministic timestamps; gaps excluded by exact joins | Canonical v2 replay exact: N=306 and stored metrics match | EXECUTABLE_PNL / EXECUTABLE_MATCH | PASS |
| H-BASIS1 | Historical event uses mark-price directional return proxy; no independently frozen exchange fill price | Exact historical Python implementation replay restored: N=156 and metrics match | FORWARD_RETURN_PROXY / PROXY_REPLAY_MATCH | PASS WITH PROXY LIMITATION |
| H-FB3 | Preregistration defines next-1m-open entry and fifth-held-1m-close exit, but exact executor artifact is not recoverable from the shared repository commit claimed by the preregistration | Result and frozen dataset identity exist; executor commit e51c4f... is not present in repository | BLOCKED_NO_CANONICAL_IMPLEMENTATION | BLOCKED |
| H-FB2 | Funding-event mark-price entry; execution fill not independently captured | Historical result retained but canonical executable implementation not reconciled | FORWARD_RETURN_PROXY | BLOCKED |
| H-FB1 / Funding-sign | Historical funding-event statistics; project-wide executable fill invariant not captured | Frozen code version and dataset metadata exist, but no executable fill contract replay | INSUFFICIENT_DATA | BLOCKED |
| 4H Momentum / Family D | Historical OHLCV momentum statistic; executable entry/exit semantics not fully reconciled to v1.1 | Result and model-run identity exist; implementation contract evidence incomplete | INSUFFICIENT_DATA | BLOCKED |
| H-SW1 | Multiple implementation lineages; funding/price agreement logic; executable fill contract not unified | Claude and Manus signatures are distinct and documented; no single executable canonical identity | BLOCKED_NO_CANONICAL_IMPLEMENTATION | BLOCKED |

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
