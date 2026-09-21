# Gate 0.5 — Historical Executable-PnL Reconciliation

Date: 2026-09-22
Decision: GATE_0_5_PASS_WITH_PROXY_LIMITATION
Trading: OFF
Hypothesis generation: PAUSED until this reconciliation is recorded

## Objective

Reconcile historical implementations against Executable PnL Contract v1.1 without changing historical results, retuning parameters, or opening new hypothesis families.

## Work executed

### H-MR1
Canonical function: research_hmr1_scan_frozen_v2(bigint,bigint,numeric,numeric,numeric)
Result: 7d34c319-f9b0-4762-99af-3b050d8975c8
Model run: c1ef915d-d0f4-4cf7-8431-e201ea2710a5
Code version: research_hmr1_scan_frozen_v2
Dataset identity: ohlcv_1m:141772;coverage_gap=84m;cutoff=1789064160000
Frozen OOS: 1785110400000 to 1789064160000
Replay: exact N=190; gross 6.9696204972 bps; net -3.0303795028 bps; stress -5.0303795028 bps; CI matched stored result.
Classification: FORWARD_RETURN_PROXY / PROXY_REPLAY_MATCH.
Reason: entry is the next available open, but the implementation permits the first available exit close in a 60–120 minute timestamp window and does not expose a separately modeled market-latency/fill contract.

### H-VOL1
Canonical function: research_hvol1_scan_frozen_v2(bigint,bigint,numeric,numeric,numeric)
Result: f538467e-3a1c-49d3-b205-12cb1fc08c59
Model run: 6d26ae2d-92c0-4745-9c67-9813d59d3906
Code version: research_hvol1_scan_frozen_v2
Dataset identity: ohlcv_1m:141772;coverage_gap=84m;cutoff=1789064160000
Frozen OOS: 1785110400000 to 1789064160000
Replay executed against the live canonical v2 function with identical frozen parameters.
Replay: N=306; gross 1.4758597311 bps; net -8.5241402689 bps; stress -10.5241402689 bps; net CI [-14.9013323141,-2.1469482237]; stress CI [-16.9013323141,-4.1469482237].
Stored result and replay match.
Classification: EXECUTABLE_PNL / EXECUTABLE_MATCH.
Reason: next-1m-open entry, exact +120m exit timestamp, explicit 10/12 bps costs, exact timestamp joins, and missing windows excluded rather than bridged. Dataset continuity has 84 missing minutes, but the implementation does not silently interpolate those windows.

### H-BASIS1
Result: 907bf0bb-9ed5-4456-94ce-cf8dda2b5e26
Historical implementation: scripts/analyze_hbasis1_mechanism.py::build_events
Historical commit: 5146f6ab173af888e23558234822627ce801a30
Dataset hash: 3ce9038421d76c3bf077dc3f5e3261a25311670286cca3801d90f113be470d79
Historical cutoff: 2026-09-10T18:16:03Z
Replay: exact N=156 and exact primary metrics.
Classification: FORWARD_RETURN_PROXY / PROXY_REPLAY_MATCH.
Reason: historical return is explicitly mark-price directional proxy; executable exchange fill prices are not part of the historical implementation.

### H-FB3
Result: 60723d89-d7f6-490e-9d2c-aea0c0c222e9
Model run: 9e680542-a3cf-4a3a-b7d3-aca381c140ea
Code version: fd712a286f4ef79476da11dcf985a8650c7008eb
Dataset hash: fc50dad316294d51f4dcde2a1d08b6450d4561cd2d9353717f1f7bfe2b215947
OOS: 2026-08-03 through 2026-09-09 UTC; cutoff 2026-09-10T10:18:00Z
Preregistration defines next-1m-open entry and fifth-held-1m-close exit, which is compatible with executable PnL. However the preregistration cites executor artifact e51c4f57600bb022374303dcfda33e0e16ff04e4, which is not present as a repository commit in the connected GitHub repository. No replacement implementation was inferred.
Classification: BLOCKED_NO_CANONICAL_IMPLEMENTATION.

### H-FB1 / Funding-sign
Result: 6bd0aa47-a6a9-4bb1-9d53-2fcc9cae7dfe
Model run: e9a03127-65c8-4943-b2b7-fbcbc061dfb0
Code version: research_funding_hfb1@20s_timeout_fix
Dataset identity: funding_rate_events:n=275;first=1780761600000;last=1788652800000
Classification: INSUFFICIENT_DATA.
Reason: historical funding-event statistics do not contain the complete executable fill invariant required by Contract v1.1.

### H-FB2
Historical result retained. No canonical executable implementation/result lineage sufficient for a v1.1 replay was identified during this pass.
Classification: FORWARD_RETURN_PROXY / BLOCKED pending implementation reconciliation.

### 4H Momentum / Family D
Result: f0c04673-c0ad-4a3a-a4eb-61b0cbced297
Model run: d5aded1f-a3cf-4cf7-8431-e201ea2710a5
Code version: research_ohlcv_momentum_nonoverlap_frozen@v1
Dataset identity: ohlcv_1m:n=563;first=1780567260000;last=1788660060000
Classification: INSUFFICIENT_DATA.
Reason: stored OHLCV momentum result exists, but the complete v1.1 entry/exit/fill evidence was not reconciled.

### H-SW1
Result: ed222262-78ef-4ee6-91ef-ab1b7b9ecde2
Model run: aaffd29c-b13e-4b2a-a2c0-a680b60300d8
Code version: research_sw1_scan_frozen@v1
Dataset identity: ohlcv_1m+funding_rate_events joint, n_candidates=91, n_signal=37
Classification: BLOCKED_NO_CANONICAL_IMPLEMENTATION.
Reason: separate Claude and Manus function lineages exist; no single executable canonical identity satisfying the contract was established.

## Gate 0.5 decision

GATE_0_5_PASS_WITH_PROXY_LIMITATION

A representative historical implementation, H-VOL1, satisfies the executable-PnL invariant and reproduces its stored result deterministically. H-MR1 and H-BASIS1 reproduce as proxy evidence, not executable PnL. Other historical families retain blockers.

This gate does not imply a profitable strategy. H-VOL1 remains economically negative: net EV -8.5241 bps, stress -10.5241 bps, CI95 entirely negative.

## Remaining blockers

1. H-FB3 executor artifact is not recoverable from the shared repository commit cited by its preregistration.
2. H-FB2/H-FB1 executable fill semantics remain incomplete.
3. Family D momentum executable entry/exit evidence remains incomplete.
4. H-SW1 has multiple implementation identities.
5. No historical result currently satisfies the project profit promotion gate.

## Authorized next action

Gate 0.5 permits the project to proceed to the data-foundation phase, but it does not authorize a new hypothesis outcome.

Next authorized engineering action:
- preserve the canonical executable-PnL engine and test fixtures;
- build immutable raw microstructure capture;
- audit OI/liquidation source semantics;
- collect observation-only data;
- do not open discovery outcomes until the observation gate and preregistration requirements are satisfied.

No new hypothesis, parameter sweep, retuning, or trading activation is authorized by this report.

Trading authorization: OFF.
