-- H-VOL1 readiness fast path. Readiness-only; no outcome scan or OOS selection.
CREATE OR REPLACE FUNCTION public.research_hvol1_readiness(
  p_as_of_ms bigint, p_oos_start_ms bigint DEFAULT NULL
)
RETURNS TABLE(
  hypothesis_key text,status text,as_of_ms bigint,oos_start_ms bigint,
  coverage_start_ms bigint,coverage_end_ms bigint,candle_count bigint,
  expected_minute_count bigint,missing_minute_count bigint,continuity_ok boolean,
  complete_range_window_count bigint,valid_taker_ratio_count bigint,
  training_candles bigint,oos_candles bigint,training_p90 numeric,training_p10 numeric,
  entry_available_count bigint,exit_available_count bigint,non_overlap_method text,
  baseline_cost_bps numeric,stress_cost_bps numeric,oos_boundary_frozen boolean,
  outcome_run boolean,authorization text
)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=public
AS $function$
BEGIN
  IF p_oos_start_ms IS NULL THEN
    RETURN QUERY
    WITH ordered AS (
      SELECT o.open_time_ms,o.volume,
             lag(o.open_time_ms,120) OVER (ORDER BY o.open_time_ms) AS prior_start_ms
      FROM public.ohlcv_1m o
      WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p_as_of_ms
    ), bounds AS (
      SELECT min(open_time_ms)::bigint AS start_ms,max(open_time_ms)::bigint AS end_ms,count(*)::bigint AS candles
      FROM ordered
    ), metrics AS (
      SELECT b.*,greatest(0,((b.end_ms-b.start_ms)/60000)+1)::bigint AS expected,
        coalesce((SELECT count(*) FROM ordered q WHERE q.prior_start_ms=q.open_time_ms-120*60000),0)::bigint AS range_count,
        coalesce((SELECT count(*) FROM ordered q WHERE q.volume>0),0)::bigint AS ratio_count
      FROM bounds b
    )
    SELECT 'H-VOL1','NOT_READY',p_as_of_ms,NULL::bigint,m.start_ms,m.end_ms,m.candles,m.expected,
      greatest(0,m.expected-m.candles),m.expected=m.candles,m.range_count,m.ratio_count,
      0::bigint,0::bigint,NULL::numeric,NULL::numeric,0::bigint,0::bigint,
      'GREEDY_CHRONOLOGICAL_PREVIOUS_ACCEPTED_EXIT',10::numeric,12::numeric,
      false,false,'NOT GRANTED'
    FROM metrics m;
    RETURN;
  END IF;

  RETURN QUERY
  WITH base AS (
    SELECT o.open_time_ms,o.volume,
      CASE WHEN o.volume>0 THEN o.taker_buy_volume/o.volume ELSE NULL END AS taker_ratio,
      lag(o.open_time_ms,120) OVER (ORDER BY o.open_time_ms) AS prior_start_ms
    FROM public.ohlcv_1m o
    WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p_as_of_ms
  ), bounds AS (
    SELECT min(open_time_ms)::bigint AS start_ms,max(open_time_ms)::bigint AS end_ms,count(*)::bigint AS candles
    FROM base
  ), coverage AS (
    SELECT b.*,greatest(0,((b.end_ms-b.start_ms)/60000)+1)::bigint AS expected FROM bounds b
  ), ratios AS (
    SELECT open_time_ms,taker_ratio FROM base WHERE taker_ratio IS NOT NULL
  ), thresholds AS (
    SELECT percentile_cont(.90) WITHIN GROUP (ORDER BY taker_ratio)::numeric AS p90,
      percentile_cont(.10) WITHIN GROUP (ORDER BY taker_ratio)::numeric AS p10
    FROM ratios WHERE open_time_ms<p_oos_start_ms
  ), metrics AS (
    SELECT c.*,p_oos_start_ms<p_as_of_ms AS boundary_frozen,
      coalesce((SELECT count(*) FROM base WHERE prior_start_ms=open_time_ms-120*60000),0)::bigint AS range_count,
      coalesce((SELECT count(*) FROM ratios),0)::bigint AS ratio_count,
      coalesce((SELECT count(*) FROM base WHERE open_time_ms<p_oos_start_ms),0)::bigint AS train_count,
      coalesce((SELECT count(*) FROM base WHERE open_time_ms>=p_oos_start_ms),0)::bigint AS oos_count,
      t.p90,t.p10,
      (SELECT count(*) FROM public.ohlcv_1m e WHERE e.symbol='BTCUSDT' AND e.interval='1m'
        AND e.open_time_ms>=p_oos_start_ms+60000 AND e.open_time_ms<=p_as_of_ms)::bigint AS entry_count,
      (SELECT count(*) FROM public.ohlcv_1m x WHERE x.symbol='BTCUSDT' AND x.interval='1m'
        AND x.open_time_ms>=p_oos_start_ms+121*60000 AND x.open_time_ms<=p_as_of_ms)::bigint AS exit_count
    FROM coverage c CROSS JOIN thresholds t
  )
  SELECT 'H-VOL1',
    CASE WHEN m.boundary_frozen AND m.expected=m.candles AND m.range_count>0 AND m.ratio_count>0
              AND m.p90 IS NOT NULL AND m.p10 IS NOT NULL
              AND m.entry_count>0 AND m.exit_count>0
         THEN 'READY_FOR_INDEPENDENT_AUDIT' ELSE 'NOT_READY' END,
    p_as_of_ms,p_oos_start_ms,m.start_ms,m.end_ms,m.candles,m.expected,
    greatest(0,m.expected-m.candles),m.expected=m.candles,m.range_count,m.ratio_count,
    m.train_count,m.oos_count,m.p90,m.p10,m.entry_count,m.exit_count,
    'GREEDY_CHRONOLOGICAL_PREVIOUS_ACCEPTED_EXIT',10::numeric,12::numeric,
    m.boundary_frozen,false,'NOT GRANTED'
  FROM metrics m;
END;
$function$;

REVOKE ALL ON FUNCTION public.research_hvol1_readiness(bigint,bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hvol1_readiness(bigint,bigint) TO anon,authenticated,service_role;
