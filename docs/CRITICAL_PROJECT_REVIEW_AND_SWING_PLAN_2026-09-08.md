# Critical Project Review and Swing Research Plan

**Date:** 2026-09-08  
**Author:** Manus AI  
**Scope:** BTCUSDT research project, H-SW1 lineage, free-tier operating constraints, and the proposed backfill versus overlap-bootstrap paths.

## Executive conclusion

The project has achieved something valuable but has not yet achieved its stated objective. It has built a reproducible research archive, a live Binance-backed observability surface, a coordination ledger, and explicit failure decisions. It has **not yet demonstrated a repeatable positive net out-of-sample edge**. The main danger is no longer missing infrastructure. The main danger is statistical and procedural: increasing the apparent sample size, adding robustness machinery after seeing an attractive point estimate, and mistaking a narrower confidence interval for more economic evidence.

The correct plan is therefore a **two-track separation**. First, preserve and verify H-SW1-CLAUDE and H-SW1-MANUS exactly as frozen historical methods. Second, if overlapping observations are scientifically justified, register a new lineage before looking at its result. That new lineage must use an explicit time-series inference procedure, a predeclared effective-sample-size rule, a temporal holdout, and a hard kill gate. The old H-SW1 functions must not be modified to rescue them.

## Evidence currently verified

| Item | Verified value | Interpretation |
|---|---:|---|
| Git source | `1153323b766c6d6255ebc9348bbf8004d3b43413` | Two methods are separated in source. |
| OHLCV rows | 138,045 BTCUSDT 1m rows | Current live coverage is approximately 96 days, not multi-year. |
| OHLCV range | `1780552860000` to `1788836640000` | The stored period is bounded and recent. |
| Funding events | 281 BTCUSDT events | Approximately 93 days at the observed cadence. |
| Claude RPC | `research_sw1_scan_frozen(text,numeric,numeric,integer)` | Exists in Supabase. |
| Manus RPC | `research_sw1_manus_scan_frozen(bigint,numeric,numeric,integer)` | Applied and verified separately. |
| Manus migration | `20260908025302` | Applied to Supabase. |
| Trading | Disabled | Neither method is an execution approval. |
| Repository state | Clean and synchronized | Git source and local clone agree. |

The RPCs have not been run in this review. Therefore, no new performance number is claimed here.

## Hard criticism of the project

### 1. Infrastructure was built before evidence justified it

The project built collectors, APIs, dashboards, deployment wiring, live audit surfaces, and multiple research RPCs before a single strategy had passed a strict out-of-sample gate. This is understandable as engineering practice, but it is backwards as a trading-research process. The repository itself calls this infrastructure debt. The dashboard is now a useful portfolio and observability artifact, but it is not evidence of predictive power.

The practical consequence is that future work must be hostile to additional building. No new dashboard surface, worker, exchange integration, or deployment should be approved merely because it makes the project feel more complete. Research output must precede product expansion.

### 2. The project has accumulated method lineages faster than independent evidence

H-FB1 and H-FB2 are killed, the funding family is closed, H-C1 is rejected, and H-SW1 now has two explicitly different implementations. Separating Claude and Manus was correct. However, two implementations are not two confirmations when they differ in candidate construction, funding agreement, and temporal grouping. They are two hypotheses.

The project must stop describing method multiplication as confirmation. A second method is useful only if it was independently specified and evaluated, not if it was created after the first method became difficult to trust.

### 3. The proposed “24× more information” argument is statistically unsafe

Moving from one daily candidate to one hourly candidate can produce approximately 24 times as many indexed rows. It does **not** produce 24 times as much independent information when each 24-hour return label overlaps the next 23 labels. Overlap creates dependence through shared price paths, shared funding events, and shared market regimes.

A block bootstrap can preserve dependence better than an IID interval, but it does not manufacture independent information. Its validity depends on a defensible block length, a stationary-enough process, a correct resampling unit, and a procedure that was specified before the result was observed. If the block length is chosen because it produces a narrower interval, the method becomes a confidence-interval tuning exercise.

The current `block_bootstrap_mean()` utility is only a generic in-memory resampler. It is not connected to H-SW1, does not estimate a block length, does not define a trading-period cluster, and does not solve the temporal holdout problem. `uniqueness_weights()` is a useful diagnostic, but weighting observations by inverse overlap count is not equivalent to a complete dependence-robust estimator or a valid economic sample-size calculation.

### 4. The existing Manus SQL contains a material specification bug

`research_sw1_manus_scan_frozen` exposes `p_funding_lookback`, but its SQL fixes `lookback_events` to `3` and limits the funding subquery to `3`. The API always passes `3`, so current output is internally consistent for the current default, but the function signature falsely suggests that the parameter is operative. This must be documented as a frozen implementation limitation or corrected only through a new lineage and migration. It must not be silently edited in place.

### 5. The current confidence intervals are not enough for overlapping labels

Both visible H-SW1 lineages summarize outcomes using variance-based intervals over rows. That is defensible only under a stated dependence assumption. It is not adequate evidence for hourly overlapping 24-hour labels. A new overlap method must report at least three views:

1. the naive row-level interval, labelled as descriptive only;
2. a dependence-robust interval using predeclared blocks or a cluster method;
3. a temporal OOS result where the decision rule was frozen before the holdout.

Only the second and third views should influence a promotion decision.

### 6. The current data horizon is too short for broad claims

The live database contains roughly three months of funding events and roughly three months of 1m OHLCV. That can support a bounded exploratory study. It cannot support a claim that a BTCUSDT swing edge is robust across multiple macro regimes. Increasing the sample inside the same regime is not the same as testing a new regime.

Backfill is therefore not useless, but it is not the immediate answer. It is an infrastructure/data-quality decision, not a rescue mechanism. Backfill should be performed only if the unchanged hypothesis has a predeclared reason to require a broader regime sample and the storage budget is explicitly measured.

## Critique of the two proposed roads

### Road A: backfill

Backfill to the free-tier boundary is reasonable as a later sensitivity exercise, but it is not sufficient as the primary plan. The proposed calculation correctly highlights diminishing precision. More observations reduce standard error approximately with the square root of effective sample size, not linearly. A 257-day window would improve precision, but it would not convert a weak or unstable mechanism into an edge.

The critical question is not whether the confidence interval becomes narrower. It is whether the net effect survives temporal splits, cost stress, and regime changes. If the answer is no, more history only proves the failure with more precision.

### Road B: overlapping windows plus block bootstrap

This is scientifically more interesting than blind backfill, but it is also the easier route for accidental self-deception. It creates more labels, increases dependence, and invites a researcher to select the block size after seeing results. It must therefore be treated as a **new hypothesis and new estimator**, not as a better CI for old H-SW1.

The correct interpretation is:

> Overlapping windows may improve temporal resolution and power for a prespecified estimator; they do not automatically increase the number of independent bets.

Road B is allowed only if its entry cadence, label horizon, funding rule, block definition, cutoff, costs, and pass/kill criteria are frozen first.

## Recommended plan

### Phase 0 — freeze the boundary

Do not run either H-SW1 RPC yet for a public conclusion. Preserve the two existing functions and record that they are verification targets. Do not edit them. Create a short preregistration for a new lineage, tentatively named `H-SW1-OVERLAP-MBB`.

The preregistration must state:

| Parameter | Required frozen choice |
|---|---|
| Entry cadence | For example, every 1 hour, not selected after results. |
| Horizon | Exactly 24 hours. |
| Candidate start | Exact Binance 1m timestamp rule. |
| Momentum definition | Exact lookback and sign rule. |
| Funding agreement | Exact number of prior completed events and unanimous/average rule. |
| Funding cashflow | Exact event inclusion interval. |
| Costs | Fee and slippage per side, plus any latency assumption. |
| Data cutoff | One timestamp selected before evaluation. |
| Discovery/OOS split | Temporal split, not random split. |
| Block unit | Time block or non-overlapping day block. |
| Block length | Predeclared from a rule, not chosen for a favorable interval. |
| Bootstrap samples | Fixed count and seed. |
| Promotion gate | Net OOS EV > 0, robust CI lower bound > 0, positive result across predeclared temporal blocks, and cost stress survival. |
| Kill gate | Any mandatory condition failing. |

### Phase 1 — run the two frozen legacy methods once

Use one common cutoff derived from the same latest stored Binance OHLCV timestamp. Invoke Claude and Manus once each. Save the exact request, raw output, function signature, cutoff, row counts, and checksums to the research vault. Do not compare only means. Compare candidate count, first/last entry, quarterly composition, direction distribution, and cost treatment.

These results answer a narrow question: **are the two existing lineages reproducible and materially different?** They do not answer whether either is a validated edge.

### Phase 2 — implement the new overlap method outside the legacy RPCs

Do not put bootstrap simulation inside the production SQL RPC. Use SQL only to emit a deterministic per-observation table or export containing:

```text
entry_time
exit_time
entry_price
exit_price
momentum_value
funding_state
raw_return_bps
funding_cashflow_bps
net_return_bps
label_interval_start
label_interval_end
```

Then run the predeclared block bootstrap in a versioned Python research script. This is easier to review, cheaper to rerun locally, and less likely to cause a long or opaque Supabase query. The SQL function should remain read-only and deterministic.

The bootstrap must preserve the time ordering inside each resampled block. The block unit should reflect the dependence created by a 24-hour label. A 24-hour block is a minimum conceptual starting point, not an automatic answer. The block length must be justified by the label horizon and, ideally, a predeclared sensitivity table such as 12h/24h/48h. Sensitivity must be reported as a robustness analysis, not selected as the winner.

### Phase 3 — validate on untouched time

Discovery may be used to check implementation and data coverage. It must not be used to select a block length, threshold, cadence, or direction. The final OOS period must remain untouched until the specification is committed.

A valid result requires all of the following:

| Gate | Requirement |
|---|---|
| Economic | Positive net EV after fees and slippage. |
| Statistical | Robust lower confidence bound above zero. |
| Temporal | Positive in each predeclared OOS block or a predeclared majority rule. |
| Cost stress | Remains positive under a conservative cost scenario. |
| Stability | No single day, week, or isolated regime explains the result. |
| Reproducibility | Independent rerun produces the same output from the same cutoff. |
| Leakage | No future data enters candidate selection, funding state, or threshold fitting. |

Failure of any mandatory gate kills the new lineage. No threshold retuning follows a failure.

### Phase 4 — only then consider paper monitoring

The dashboard should not receive a new swing signal panel before the new lineage passes validation. If it passes, expose only aggregate public metrics and `trading_enabled: false`. Keep the method, thresholds, and per-trade evidence private unless the owner deliberately changes the disclosure policy.

## Operational solutions beyond research statistics

The project needs a stricter separation of layers:

| Layer | What belongs there | What must be prohibited |
|---|---|---|
| Data | Binance ingestion, gap checks, retention metrics | Unbounded backfill and mixed-source contamination |
| Research | Frozen specs, raw outcomes, OOS tests | UI-driven hypothesis changes |
| Inference | Block/cluster methods, sensitivity, uncertainty | Choosing blocks after seeing results |
| Product | Archive, health, aggregate metrics | Signal theatre and decorative widgets |
| Execution | Disabled until promotion | Any order path before independent paper validation |

The ledger also needs a mandatory evidence bundle for every completed run: specification hash, Git commit, migration version, cutoff, query signature, raw output checksum, summary output, and decision. `claimed_done` must never substitute for this bundle.

## What should happen now

The immediate next action is **not** to backfill and not to run the overlap scan. The immediate action is to create and review the preregistration for `H-SW1-OVERLAP-MBB`, while separately preparing one-shot legacy verification at a common cutoff. Once that specification is frozen, run the two legacy RPCs once, then run the new method only as its own lineage.

This order prevents three common failures:

1. using a new estimator to rescue an old result;
2. treating correlated overlapping labels as independent trades;
3. making the dashboard look more certain than the research actually is.

## Final judgment

The project is technically disciplined in provenance and operational memory, but it is currently **overbuilt relative to its validated evidence and under-specified relative to its statistical ambition**. The strongest asset is the refusal to fabricate results and the existence of a durable ledger. The greatest weakness is the temptation to keep adding methods, panels, and statistical machinery until one produces a persuasive number.

The solution is not more cleverness. It is a smaller number of frozen experiments, stronger uncertainty accounting, untouched temporal holdouts, and automatic killing of anything that fails. If the overlap method survives those constraints, it becomes a credible research result. If it fails, that failure is valuable and the next hypothesis should be genuinely different—not a new confidence interval for the same story.

## References

[1]: https://github.com/Pfn17/btc-usdt-research2/blob/1153323b766c6d6255ebc9348bbf8004d3b43413/docs/AGENT_HANDOFF_2026-09-08_TWO_METHODS.md "Two-method H-SW1 verification handoff"
[2]: https://github.com/Pfn17/btc-usdt-research2/blob/1153323b766c6d6255ebc9348bbf8004d3b43413/supabase/migrations/20260908_hsw1_swing_lite.sql "H-SW1-Manus frozen migration"
[3]: https://github.com/Pfn17/btc-usdt-research2/blob/1153323b766c6d6255ebc9348bbf8004d3b43413/src/btc_research/research/robustness.py "Project robustness utilities"
[4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC4443935/ "Moving block bootstrap for dependent observations"
[5]: https://mlfinpy.readthedocs.io/en/latest/Sampling.html "Sampling and label uniqueness in financial machine learning"
