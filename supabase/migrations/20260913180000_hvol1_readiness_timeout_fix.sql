-- H-VOL1 readiness timeout fix.
-- Readiness-only: no profitability scan, no outcome, no cutoff selection.
-- Replaces the O(N*120) self-join with ordered timestamp/window computation.
CREATE OR REPLACE FUNCTION public.research_hvol1_readiness(
  p_as_of_ms bigint,
  p_oos_start_ms bigint DEFAULT NULL
)
RETURNS TABLE(
  hypothesis_key text,
  status text,
  as_of_ms bigint,
  oos_start_ms bigint,
  coverage_start_ms bigint,
  coverage_end_ms bigint,
  candle_count bigint,
  expected_minute_count bigint,
  missing_minute_count bigint,
  continuity_ok boolean,
  complete_range_window_count bigint,
  valid_taker_ratio_count bigint,
  training_candles bigint,
  oos_candles bigint,
  training_p90 numeric,
  training_p10 numeric,
  entry_available_count bigint,
  exit_available_count bigint,
  non_overlap_method text,
  baseline_cost_bps numeric,
  stress_cost_bps numeric,
  oos_boundary_frozen boolean,
  outcome_run boolean,
  authorization text
)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
AS $function$
WITH base AS (
  SELECT o.open_time_ms, o.high, o.low, o.close, o.volume,
         CASE WHEN o.volume > 0 THEN o.taker_buy_volume / o.volume ELSE NULL END AS taker_ratio,
         lag(o.open_time_ms, 120) OVER (ORDER BY o.open_time_ms) AS prior_start_ms,
         max(o.high) OVER (ORDER BY o.open_time_ms ROWS BETWEEN 120 PRECEDING AND 1 PRECEDING) AS prior_high,
         min(o.low) OVER (ORDER BY o.open_time_ms ROWS BETWEEN 120 PRECEDING AND 1 PRECEDING) AS prior_low
  FROM public.ohlcv_1m o
  WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p_as_of_ms
), bounds AS (
  SELECT min(open_time_ms)::bigint AS start_ms, max(open_time_ms)::bigint AS end_ms,
         count(*)::bigint AS candles
  FROM base
), coverage AS (
  SELECT b.*, greatest(0, ((b.end_ms-b.start_ms)/60000)+1)::bigint AS expected
  FROM bounds b
), ratios AS (
  SELECT open_time_ms, taker_ratio FROM base WHERE taker_ratio IS NOT NULL
), thresholds AS (
  SELECT percentile_cont(.90) WITHIN GROUP (ORDER BY taker_ratio) AS p90,
         percentile_cont(.10) WITHIN GROUP (ORDER BY taker_ratio) AS p10
  FROM ratios WHERE p_oos_start_ms IS NOT NULL AND open_time_ms < p_oos_start_ms
), candidates AS (
  SELECT b.open_time_ms AS trigger_ms
  FROM base b CROSS JOIN thresholds t
  WHERE p_oos_start_ms IS NOT NULL
    AND b.open_time_ms >= p_oos_start_ms
    AND b.open_time_ms < p_as_of_ms
    AND b.prior_start_ms = b.open_time_ms - 120*60000
    AND b.taker_ratio IS NOT NULL
    AND ((b.close > b.prior_high AND b.taker_ratio >= t.p90)
      OR (b.close < b.prior_low AND b.taker_ratio <= t.p10))
), availability AS (
  SELECT count(*) FILTER (
           WHERE EXISTS (SELECT 1 FROM base e WHERE e.open_time_ms=c.trigger_ms+60000)
         )::bigint AS entry_count,
         count(*) FILTER (
           WHERE EXISTS (SELECT 1 FROM base e WHERE e.open_time_ms=c.trigger_ms+60000)
             AND EXISTS (SELECT 1 FROM base x WHERE x.open_time_ms=c.trigger_ms+121*60000)
         )::bigint AS exit_count
  FROM candidates c
), metrics AS (
  SELECT c.*, p_oos_start_ms IS NOT NULL AND p_oos_start_ms < p_as_of_ms AS boundary_frozen,
    coalesce((SELECT count(*) FROM base WHERE prior_start_ms=open_time_ms-120*60000),0)::bigint AS range_count,
    coalesce((SELECT count(*) FROM ratios),0)::bigint AS ratio_count,
    coalesce((SELECT count(*) FROM base WHERE p_oos_start_ms IS NOT NULL AND open_time_ms<p_oos_start_ms),0)::bigint AS train_count,
    coalesce((SELECT count(*) FROM base WHERE p_oos_start_ms IS NOT NULL AND open_time_ms>=p_oos_start_ms),0)::bigint AS oos_count,
    t.p90, t.p10, a.entry_count, a.exit_count
  FROM coverage c CROSS JOIN thresholds t CROSS JOIN availability a
)
SELECT 'H-VOL1',
  CASE WHEN m.boundary_frozen AND m.range_count>0 AND m.ratio_count>0
             AND m.p90 IS NOT NULL AND m.p10 IS NOT NULL
             AND m.entry_count>0 AND m.exit_count>0
       THEN 'READY_FOR_INDEPENDENT_AUDIT' ELSE 'NOT_READY' END,
  p_as_of_ms,p_oos_start_ms,m.start_ms,m.end_ms,m.candles,m.expected,
  greatest(0,m.expected-m.candles),m.expected=m.candles,m.range_count,
  m.ratio_count,m.train_count,m.oos_count,m.p90,m.p10,m.entry_count,m.exit_count,
  'GREEDY_CHRONOLOGICAL_PREVIOUS_ACCEPTED_EXIT',10::numeric,12::numeric,
  m.boundary_frozen,false,'NOT GRANTED'
FROM metrics m;
$function$;

REVOKE ALL ON FUNCTION public.research_hvol1_readiness(bigint,bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hvol1_readiness(bigint,bigint) TO anon, authenticated, service_role;
