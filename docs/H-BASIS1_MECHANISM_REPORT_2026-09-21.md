# H-BASIS1 Mechanism Research Report

## H-BASIS1 STATUS

**INCONCLUSIVE / UNDERPOWERED.** H-BASIS1 does not qualify as a trading edge or promotion candidate. The frozen primary mechanism study found weak convergence and negative mark-price proxy economics in the holdout period. The OOS holdout contains only three active UTC days, below the preregistered minimum of five active days for a mechanism conclusion. The result is therefore not labeled `PASS` or `KILLED`; it is an underpowered negative indication that should not be promoted or retuned on this dataset.

## Data verified

The analysis used the real `public.funding_basis_snapshots` table for `BTCUSDT`. The frozen extract contains **10,510 rows** and **10,510 distinct timestamps**. All rows had valid `mark_price`, `index_price`, and generated `basis_bps` values. The data spans `2026-09-03T04:34:56Z` through `2026-09-10T18:16:03Z`.

The median inter-snapshot interval is **60,998 ms**. There are **12 gaps longer than five minutes**, and the maximum observed gap is **1,924,000 ms**. No values were bridged. Entry, exit, and convergence observations were matched only to actual timestamps within the frozen tolerance.

The raw dataset hash is:

```text
3ce9038421d76c3bf077dc3f5e3261a25311670286cca3801d90f113be470d79
```

## Mechanism tested

H-BASIS1 defines `basis_bps` as the stored mark-to-index basis. The reference level is the median basis over the preceding six elapsed hours, requiring at least 30 preceding snapshots. The residual is current basis minus that local median.

The signal universe was frozen before the event-level calculation. A candidate is an absolute residual at or above the train-only 90th percentile. The frozen threshold was **1.551082 bps**. The proxy direction is short when the residual is positive and long when it is negative.

The primary event uses a one-minute minimum entry delay and a **15-minute** horizon. The predeclared sensitivity horizons are **5, 30, and 60 minutes**. Events are accepted chronologically and cannot overlap a previously scheduled exit. Missing entry or exit timestamps are censored rather than filled.

A convergence event requires the absolute exit residual to be no more than half the absolute entry residual. A sign-crossing is reported separately. This convergence definition is not treated as equivalent to executable profit.

## Primary 15-minute result

The OOS holdout is `2026-09-08T00:00:00Z` through `2026-09-10T18:16:03Z`. It produced **156 accepted events across three active UTC days**. The 50% convergence rate was **33.97%**, with a one-day block-bootstrap interval of **19.87% to 48.08%**. The point estimate is below the preregistered 50% mechanism criterion, and the interval does not demonstrate positive convergence above that criterion.

The mark-price proxy produced a mean gross return of **−1.10 bps**. After the fixed 10 bps round-trip cost, mean net proxy return was **−11.10 bps**. The 12 bps stress result was **−13.10 bps**. The one-day block-bootstrap 95% interval for mean net proxy return was **[−13.53, −8.55] bps**. These values are non-executable diagnostics because the dataset contains no tradeable bid/ask fills or market-impact model.

Median time to 50% convergence among converged events was approximately **2.02 minutes**. No primary-horizon exits were censored under the frozen two-minute exit tolerance. Mean adverse excursion was approximately **−0.72 bps** under the directional price proxy.

## Horizon sensitivity

The sensitivity cells were frozen in advance and are shown without selecting a winner.

| Horizon | OOS events | Active days | Mean gross proxy (bps) | Mean net at 10 bps (bps) | Stress at 12 bps (bps) | 50% convergence rate | Net CI95, day-block bootstrap (bps) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 minutes | 282 | 3 | 0.14 | −9.86 | −11.86 | 34.04% | [−11.13, −9.01] |
| 15 minutes | 156 | 3 | −1.10 | −11.10 | −13.10 | 33.97% | [−13.53, −8.55] |
| 30 minutes | 100 | 3 | −1.83 | −11.83 | −13.83 | 44.00% | [−13.09, −11.24] |
| 60 minutes | 56 | 3 | −4.79 | −14.79 | −16.79 | 44.64% | [−26.68, −7.33] |

The sensitivity table does not provide evidence of a cost-adjusted mechanism. All four horizons have negative mean net proxy returns, and all have negative bootstrap intervals in this analysis. The convergence rates remain below 50% at every frozen horizon.

For the primary 15-minute OOS cell, the predeclared block-length sensitivity remained negative: the 12-hour block interval was **[−11.58, −7.78] bps**, and the 48-hour block interval was **[−10.39, −9.61] bps**. These sensitivity intervals were recorded descriptively and were not used to select a horizon or a decision.

## Persistence and distribution diagnostics

The raw basis distribution is strongly asymmetric over this short collection window. Its median is **−4.2902 bps**, with the 1st and 99th percentiles at approximately **−6.6914 bps** and **−1.2854 bps**. This is why the specification uses a local six-hour baseline rather than a zero-centered basis rule.

The residual autocorrelation for adjacent observations whose timestamps are no more than two minutes apart is approximately **0.496** across **10,356** valid pairs. This supports treating nearby snapshots as dependent observations. The event non-overlap rule and day-block bootstrap were therefore used instead of treating all snapshots as independent.

The results do not show sufficient convergence consistency. The OOS day means were negative at the 5-minute, 15-minute, 30-minute, and 60-minute horizons, although the three-day holdout is too short for a broad regime claim.

## Decision and limitations

H-BASIS1 is **INCONCLUSIVE / UNDERPOWERED** under its preregistered mechanism gate because the holdout contains only three active UTC days rather than the required five. The evidence is nevertheless unfavorable: convergence is below the 50% criterion and the fixed-cost mark-price proxy is negative at every frozen horizon.

This result is not a claim that basis convergence never occurs. It shows that this frozen six-hour-residual definition did not demonstrate sufficiently reliable convergence or cost-adjusted economics in the available holdout. No threshold, baseline, horizon, or exit rule was retuned after viewing the results. Any follow-up would require a new hypothesis identity and a new preregistration rather than a modification of H-BASIS1.

Trading authorization remains **OFF**. No order path was added or enabled. No prior H-MR1, H-VOL1, H-SW1, or H-FB family OOS result was reused as H-BASIS1 evidence.

## Freeze and provenance metadata

- Specification hash: `f9b3c6cefc7986c6785d2cb4c3434ba6fb834a888ad7bf8fbf3f6d324198c08e`.
- Dataset hash: `3ce9038421d76c3bf077dc3f5e3261a25311670286cca3801d90f113be470d79`.
- Mechanism script: `scripts/analyze_hbasis1_mechanism.py` in commit `5146f6a`; it reproduces the committed analysis artifact from the frozen raw extract.
- Bootstrap: 2,000 resamples, UTC-day event blocks, seed `20260921`, percentile interval.
- Cost model: 4 bps fee per side plus 1 bps slippage per side; 10 bps baseline round trip and 12 bps stress.
- Outcome classification: mechanism-stage `INCONCLUSIVE / UNDERPOWERED`; no promotion or production readiness claim.

## References

[1]: https://github.com/Pfn17/btc-usdt-research2 "BTCUSDT Research 2 repository"
