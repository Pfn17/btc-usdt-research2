# Regression gate — 2026-09-22

Run ID: `FORENSIC-GATE-2026-09-22`

## Tests

| Test | Expected | Observed | Result |
|---|---|---|---|
| Synthetic known positive | PASS | PASS | PASS |
| Synthetic below cost | KILL | KILL | PASS |
| Synthetic leakage | REJECT | REJECT | PASS |
| Synthetic train-only edge failing OOS | KILL | KILL | PASS |
| Canonical H-MR1 replay | MATCH | MATCH | PASS |
| Canonical H-BASIS1 replay | MATCH | MISMATCH | **FAIL** |

## Gate state

**BLOCKED**

The decision-path harness itself passes, and H-MR1 reproduces exactly. The gate remains blocked because H-BASIS1 cannot be reproduced from the current canonical RPC.

The next action is provenance recovery for H-BASIS1, not a new hypothesis and not a parameter adjustment.

Historical evidence remains append-only. Trading remains OFF.
