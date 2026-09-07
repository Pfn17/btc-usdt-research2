# Lite Swing Trading: Free-Tier Implementation Plan

## Executive decision

Lite swing trading should begin as a **research harness**, not as a signal engine or execution bot. The current repository and Supabase project do not contain an official, committed H-SW1 specification or a swing RPC function. The externally reported H-SW1 result is explicitly unverified and must not be implemented or retuned. The next valid step is to freeze one new swing hypothesis, run one bounded discovery/validation batch, and preserve the complete lineage.

The implementation should reuse the existing BTCUSDT 1-minute OHLCV and funding-event tables. It should not add a new collector, a new Railway service, a price chart, a WebSocket, or a continuous swing scheduler. A swing experiment can be evaluated with a single manual or explicitly authorized batch query because its holding horizon is measured in hours or days.

## Observed capacity boundary

The live audit observed approximately 137,394 BTCUSDT 1-minute OHLCV rows and 279 funding events. The observed OHLCV range was about 95 days, and the funding range was about 93 days. These values are an input constraint, not a promise of future availability. A 24-hour non-overlapping design can produce at most roughly one hundred candidate observations from this window before filters and missing data reduce the count. That sample size is likely underpowered for a narrow confidence interval.

The free-tier design therefore avoids storing derived candles, feature snapshots, equity curves, or duplicate event tables. Higher timeframes must be derived inside one bounded SQL/RPC call from existing OHLCV rows or in a local, disposable calculation. Only the frozen specification, dataset identity, aggregate result, and decision evidence belong in Git and the research registry.

## System boundary

| Component | Lite-swing behavior | Free-tier reason |
|---|---|---|
| Raw OHLCV | Reuse `public.ohlcv_1m`; refetchable input | No duplicate storage |
| Funding events | Reuse `public.funding_rate_events` only if preregistered as a feature | Existing small table; no new feed |
| Feature calculation | One bounded SQL/RPC batch | No continuous compute |
| Experiment registry | Reuse `experiment_families`, `research_hypotheses`, `experiment_batches`, `model_runs`, `research_results`, and `cost_models` | Existing schema is the source of truth |
| Research output | Aggregate rows plus confidence, stability, and period concentration | No per-candidate persistence unless required for audit |
| API | No route until a candidate passes the validation gate | Avoid premature production surface |
| Dashboard | No swing signal; show only persisted research status after verification | Prevent stale or hardcoded claims |
| Execution | Permanently disabled in this phase | Research-only boundary |
| Scheduler | None for discovery; at most an owner-approved low-frequency forward paper check later | Avoid Manus and provider quota burn |

## Required preregistration

Before any result query, the owner must approve a new experiment family and hypothesis identifier. The specification must freeze the mechanism, feature definitions, data universe, timestamp cutoff, entry rule, exit rule, holding horizon, direction rule, funding treatment, fee, spread, slippage, latency, train/OOS split, purge rule, embargo rule, minimum sample, confidence method, stability gate, and kill/promote criteria.

The hypothesis must be materially different from the unverified H-SW1 claim. It must not reuse a 24-hour rule and then change only the lookback, funding count, horizon, direction, or period split after observing a result. Such a change is a new hypothesis and requires a new lineage.

## Candidate design choices

The following are design choices for owner approval. They are not results and must not be run until one is frozen.

| Choice | Mechanism | Data cost | Main risk | Recommendation |
|---|---|---:|---|---|
| A. Daily trend continuation | Prior completed 24-hour return defines direction; entry at the next eligible daily boundary; exit after a fixed 24-hour hold | Very low | Approximately 95 days yields too few independent observations | Use only if the objective is a minimal harness smoke test |
| B. Multi-hour breakout continuation | A fixed completed lookback range defines direction; enter only after a fixed breakout condition; exit after a fixed multi-hour hold | Low | More rule knobs create selection risk | Better candidate if every knob is frozen before testing |
| C. Volatility-normalized reversal | A fixed extreme move is faded after a fixed cooldown; exit after a fixed hold or barrier | Low | Threshold and regime dependence can create multiple-testing bias | Do not use without a strong mechanism and one frozen threshold |

The existing ledger does not authorize selecting one of these on behalf of the owner. The safe default is **Choice A as a harness smoke test only**, not as a presumed edge. If the owner wants a potentially more informative experiment, select one alternative and write its exact frozen numbers first.

## Evaluation sequence

The sequence must be chronological and one-directional.

1. **Register.** Insert one new family, one hypothesis, one cost model, and one frozen batch before inspecting the outcome.
2. **Identify data.** Record source tables, minimum and maximum timestamps, row counts, gaps, cutoff timestamp, and a deterministic dataset/configuration hash.
3. **Discover.** Run exactly one bounded query on the discovery segment. Discovery may reject the mechanism; it may not be used to tune parameters.
4. **Validate.** Run the unchanged rule on an untouched chronological OOS segment. Use non-overlapping observations where the holding period requires it.
5. **Measure.** Record gross EV, net EV, hit rate, confidence interval, maximum drawdown if applicable, period concentration, and regime stability. Include costs in the primary result.
6. **Decide.** Apply the preregistered gate. A non-positive net EV, a confidence interval crossing zero, material period instability, or insufficient sample produces `KILLED` or `INCONCLUSIVE`, never a promoted signal.
7. **Verify.** A different agent or the owner independently checks the registry row, function definition, invocation, cutoff, output, and commit.
8. **Persist.** Commit the specification, migration/RPC source if any, result export, and evidence before beginning another batch.

## Proposed bounded implementation

If a new hypothesis is approved, implementation should consist of one versioned migration containing one immutable, read-only research RPC. The RPC should accept only the frozen cutoff and a bounded sample limit. It should derive the required higher-timeframe bars from `ohlcv_1m`, select non-overlapping candidates by recursive skip-ahead or an equivalent deterministic method, apply the frozen entry and exit rules, subtract the frozen cost model, and return aggregate metrics plus period buckets.

The RPC must reject invalid horizons and sample limits. It must not write market data, signals, orders, or dashboard state. It must not read the current wall-clock time to change the sample. The cutoff must be explicit so the same call is replayable.

The first implementation should not add a production API route. A direct Supabase call is cheaper and easier to audit. An API route becomes justified only after the candidate passes Stage 2 and enters forward paper validation.

## Forward paper phase after a pass

A passing backtest does not activate trading. The next phase would be a low-frequency paper monitor that evaluates only at the experiment's decision boundary, for example once per completed holding interval. It would write at most one paper observation per eligible interval and would retain only the fields needed for verification. It would not place orders, poll every second, or create a new market-data collector.

A forward paper phase requires a separate approval, a new ledger task, a retention limit, and a free-tier budget check. If the candidate fails forward paper validation, it is killed and the paper monitor is stopped.

## Recovery and account replacement

The Git repository remains the durable source of truth for the swing specification, migration, RPC source, configuration hash, dataset provenance, result export, and decision. A replacement Supabase project should be rebuilt from versioned migrations and then refetched only for the timestamp window required by the active experiment. Secrets are recreated manually and never restored from Git.

## Current stop condition

No swing RPC, signal, API endpoint, scheduler, or dashboard badge should be implemented until the owner selects and approves one frozen hypothesis. The current H-SW1 report remains `UNVERIFIED` in the repository, and its reported positive point estimate is not evidence of an edge.

## References

[1]: https://github.com/Pfn17/btc-usdt-research2/blob/main/docs/EXPERIMENT_LEDGER.md "BTCUSDT Edge Research Experiment Ledger"

[2]: https://github.com/Pfn17/btc-usdt-research2/blob/main/docs/FREE_TIER_GOVERNANCE.md "HyperHan Lab Free-Tier Governance"

[3]: https://github.com/Pfn17/btc-usdt-research2/blob/main/docs/AGENT_HANDOFF_2026-09-07.md "Agent Handoff and Swing Research Boundary"

[4]: https://github.com/Pfn17/btc-usdt-research2/blob/main/docs/EXTERNAL_RESEARCH_REPORT_2026-09-07.md "External H-SW1 Verification Boundary"
