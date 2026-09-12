-- H-VOL1: breakout confirmed by extreme taker-flow participation.
-- Read-only research objects. This migration defines methodology only; it does not execute an outcome scan.
-- The live registry already contains this lineage under migrations 20260912075810,
-- 20260912075927, and 20260912080008. This file reconciles the source into GitHub.

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
WITH params AS (
  SELECT p_as_of_ms::bigint AS as_of_ms, p_oos_start_ms::bigint AS oos_start_ms
), bounds AS (
  SELECT min(o.open_time_ms)::bigint AS start_ms,
         max(o.open_time_ms)::bigint AS end_ms,
         count(*)::bigint AS candles
  FROM public.ohlcv_1m o CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p.as_of_ms
), coverage AS (
  SELECT b.*, greatest(0, ((b.end_ms-b.start_ms)/60000)+1)::bigint AS expected
  FROM bounds b
), range_windows AS (
  SELECT o.open_time_ms AS trigger_ms,
         count(w.open_time_ms)::bigint AS prior_count,
         min(w.open_time_ms)::bigint AS prior_first_ms,
         max(w.open_time_ms)::bigint AS prior_last_ms
  FROM public.ohlcv_1m o
  JOIN public.ohlcv_1m w
    ON w.symbol=o.symbol AND w.interval=o.interval
   AND w.open_time_ms>=o.open_time_ms-120*60*1000
   AND w.open_time_ms<o.open_time_ms
  CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p.as_of_ms
  GROUP BY o.open_time_ms
), ratios AS (
  SELECT o.open_time_ms,
         CASE WHEN o.volume>0 THEN o.taker_buy_volume/o.volume ELSE NULL END AS taker_ratio
  FROM public.ohlcv_1m o CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p.as_of_ms
), thresholds AS (
  SELECT percentile_cont(.90) WITHIN GROUP (ORDER BY taker_ratio) AS p90,
         percentile_cont(.10) WITHIN GROUP (ORDER BY taker_ratio) AS p10
  FROM ratios r CROSS JOIN params p
  WHERE r.taker_ratio IS NOT NULL AND p.oos_start_ms IS NOT NULL
    AND r.open_time_ms<p.oos_start_ms
), entry AS (
  SELECT count(*)::bigint AS n
  FROM public.ohlcv_1m o CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND p.oos_start_ms IS NOT NULL
    AND o.open_time_ms>=p.oos_start_ms+60000 AND o.open_time_ms<=p.as_of_ms
), exit_data AS (
  SELECT count(*)::bigint AS n
  FROM public.ohlcv_1m o CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND p.oos_start_ms IS NOT NULL
    AND o.open_time_ms>=p.oos_start_ms+121*60000 AND o.open_time_ms<=p.as_of_ms
), counts AS (
  SELECT c.*,
    coalesce((SELECT count(*) FROM range_windows
      WHERE prior_count=120
        AND prior_first_ms=trigger_ms-120*60*1000
        AND prior_last_ms=trigger_ms-60*1000),0)::bigint AS range_count,
    coalesce((SELECT count(*) FROM ratios WHERE taker_ratio IS NOT NULL),0)::bigint AS ratio_count,
    coalesce((SELECT count(*) FROM ratios r,params p
      WHERE p.oos_start_ms IS NOT NULL AND r.open_time_ms<p.oos_start_ms),0)::bigint AS train_count,
    coalesce((SELECT count(*) FROM ratios r,params p
      WHERE p.oos_start_ms IS NOT NULL AND r.open_time_ms>=p.oos_start_ms),0)::bigint AS oos_count,
    (SELECT n FROM entry) AS entry_count,
    (SELECT n FROM exit_data) AS exit_count,
    (SELECT p90 FROM thresholds) AS p90,
    (SELECT p10 FROM thresholds) AS p10
  FROM coverage c
), flags AS (
  SELECT x.*, p.oos_start_ms, p.as_of_ms,
         (p.oos_start_ms IS NOT NULL AND p.oos_start_ms<p.as_of_ms) AS boundary_frozen
  FROM counts x CROSS JOIN params p
)
SELECT 'H-VOL1',
  CASE WHEN f.boundary_frozen AND f.range_count>0 AND f.ratio_count>0
             AND f.p90 IS NOT NULL AND f.p10 IS NOT NULL
             AND f.entry_count>0 AND f.exit_count>0
       THEN 'READY_FOR_INDEPENDENT_AUDIT' ELSE 'NOT_READY' END,
  f.as_of_ms,f.oos_start_ms,f.start_ms,f.end_ms,f.candles,f.expected,
  greatest(0,f.expected-f.candles),f.expected=f.candles,f.range_count,
  f.ratio_count,f.train_count,f.oos_count,f.p90,f.p10,f.entry_count,f.exit_count,
  'GREEDY_CHRONOLOGICAL_PREVIOUS_ACCEPTED_EXIT',10::numeric,12::numeric,
  f.boundary_frozen,false,'NOT GRANTED'
FROM flags f;
$function$;

-- Manual future outcome function. It is never called by the dashboard.
CREATE OR REPLACE FUNCTION public.research_hvol1_scan_frozen(
  p_oos_start_ms bigint,
  p_as_of_ms bigint,
  p_fee_bps numeric DEFAULT 4,
  p_slippage_bps numeric DEFAULT 1,
  p_stress_round_trip_bps numeric DEFAULT 12
)
RETURNS TABLE(
  bucket text,
  direction text,
  n bigint,
  mean_gross_bps numeric,
  mean_net_bps numeric,
  mean_stress_net_bps numeric,
  win_rate numeric,
  net_ci95_low numeric,
  net_ci95_high numeric,
  stress_ci95_low numeric,
  stress_ci95_high numeric,
  positive_weeks bigint,
  total_weeks bigint,
  max_positive_week_share numeric,
  threshold_p90 numeric,
  threshold_p10 numeric,
  first_entry_ms bigint,
  last_entry_ms bigint
)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
AS $function$
WITH RECURSIVE params AS (
  SELECT p_oos_start_ms::bigint AS oos_start_ms,p_as_of_ms::bigint AS as_of_ms,
    greatest(0,p_fee_bps)::numeric AS fee_bps,
    greatest(0,p_slippage_bps)::numeric AS slippage_bps,
    greatest(0,p_stress_round_trip_bps)::numeric AS stress_rt_bps
), base AS (
  SELECT o.open_time_ms AS trigger_ms,o.close,o.high,o.low,
    CASE WHEN o.volume>0 THEN o.taker_buy_volume/o.volume ELSE NULL END AS taker_ratio
  FROM public.ohlcv_1m o CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms<=p.as_of_ms
), range_windows AS (
  SELECT b.trigger_ms,b.close,b.high,b.low,b.taker_ratio,
    max(w.high) AS prior_high,min(w.low) AS prior_low,
    count(w.open_time_ms)::bigint AS prior_count,
    min(w.open_time_ms)::bigint AS prior_first_ms,
    max(w.open_time_ms)::bigint AS prior_last_ms
  FROM base b JOIN public.ohlcv_1m w
    ON w.symbol='BTCUSDT' AND w.interval='1m'
   AND w.open_time_ms>=b.trigger_ms-120*60*1000
   AND w.open_time_ms<b.trigger_ms
  GROUP BY b.trigger_ms,b.close,b.high,b.low,b.taker_ratio
), ratios AS (
  SELECT b.trigger_ms,b.taker_ratio FROM base b WHERE b.taker_ratio IS NOT NULL
), thresholds AS (
  SELECT percentile_cont(.90) WITHIN GROUP (ORDER BY r.taker_ratio) AS p90,
    percentile_cont(.10) WITHIN GROUP (ORDER BY r.taker_ratio) AS p10
  FROM ratios r CROSS JOIN params p WHERE r.trigger_ms<p.oos_start_ms
), raw_candidates AS (
  SELECT rw.trigger_ms,
    CASE WHEN rw.close>rw.prior_high THEN 'LONG' ELSE 'SHORT' END AS direction
  FROM range_windows rw CROSS JOIN params p CROSS JOIN thresholds t
  WHERE rw.prior_count=120
    AND rw.prior_first_ms=rw.trigger_ms-120*60*1000
    AND rw.prior_last_ms=rw.trigger_ms-60*1000
    AND rw.taker_ratio IS NOT NULL
    AND rw.trigger_ms>=p.oos_start_ms AND rw.trigger_ms<p.as_of_ms
    AND ((rw.close>rw.prior_high AND rw.taker_ratio>=t.p90)
      OR (rw.close<rw.prior_low AND rw.taker_ratio<=t.p10))
), with_fills AS (
  SELECT c.trigger_ms,c.direction,e.open_time_ms AS entry_ms,e.open AS entry_price,
    x.open_time_ms AS exit_ms,x.close AS exit_price
  FROM raw_candidates c
  JOIN public.ohlcv_1m e ON e.symbol='BTCUSDT' AND e.interval='1m'
    AND e.open_time_ms=c.trigger_ms+60000
  JOIN public.ohlcv_1m x ON x.symbol='BTCUSDT' AND x.interval='1m'
    AND x.open_time_ms=e.open_time_ms+120*60*1000
), ordered_fills AS (
  SELECT f.*,row_number() OVER (ORDER BY f.entry_ms,f.trigger_ms) AS candidate_no
  FROM with_fills f
), greedy AS (
  SELECT f.* FROM ordered_fills f WHERE f.candidate_no=1
  UNION ALL
  SELECT next_f.* FROM greedy accepted
  CROSS JOIN LATERAL (
    SELECT f.* FROM ordered_fills f
    WHERE f.entry_ms>=accepted.exit_ms
    ORDER BY f.entry_ms,f.trigger_ms LIMIT 1
  ) next_f
), scored AS (
  SELECT g.*,10000.0*(CASE WHEN g.direction='LONG' THEN 1 ELSE -1 END)
    *(g.exit_price-g.entry_price)/NULLIF(g.entry_price,0) AS gross_bps
  FROM greedy g
), net AS (
  SELECT s.*,s.gross_bps-2*(p.fee_bps+p.slippage_bps) AS net_bps,
    s.gross_bps-p.stress_rt_bps AS stress_net_bps,
    extract(isoyear FROM to_timestamp(s.entry_ms/1000.0))::int AS iso_year,
    extract(week FROM to_timestamp(s.entry_ms/1000.0))::int AS iso_week
  FROM scored s CROSS JOIN params p
), week_stats AS (
  SELECT iso_year,iso_week,avg(net_bps) AS week_net,
    sum(greatest(net_bps,0)) AS positive_contribution
  FROM net GROUP BY iso_year,iso_week
), rows AS (
  SELECT 'overall'::text bucket,'ALL'::text direction,n.trigger_ms,n.entry_ms,n.entry_price,n.exit_ms,n.exit_price,n.gross_bps,n.net_bps,n.stress_net_bps,n.iso_year,n.iso_week FROM net n
  UNION ALL SELECT 'week_'||iso_year||'_W'||lpad(iso_week::text,2,'0'),'ALL',n.trigger_ms,n.entry_ms,n.entry_price,n.exit_ms,n.exit_price,n.gross_bps,n.net_bps,n.stress_net_bps,n.iso_year,n.iso_week FROM net n
  UNION ALL SELECT 'direction'::text,n.direction,n.trigger_ms,n.entry_ms,n.entry_price,n.exit_ms,n.exit_price,n.gross_bps,n.net_bps,n.stress_net_bps,n.iso_year,n.iso_week FROM net n
), stats AS (
  SELECT r.bucket,r.direction,count(*)::bigint AS n,avg(r.gross_bps) AS mean_gross_bps,
    avg(r.net_bps) AS mean_net_bps,avg(r.stress_net_bps) AS mean_stress_net_bps,
    avg((r.net_bps>0)::int)::numeric AS win_rate,
    avg(r.net_bps)-1.96*sqrt(greatest(0,coalesce(variance(r.net_bps),0))/nullif(count(*),0)) AS net_ci95_low,
    avg(r.net_bps)+1.96*sqrt(greatest(0,coalesce(variance(r.net_bps),0))/nullif(count(*),0)) AS net_ci95_high,
    avg(r.stress_net_bps)-1.96*sqrt(greatest(0,coalesce(variance(r.stress_net_bps),0))/nullif(count(*),0)) AS stress_ci95_low,
    avg(r.stress_net_bps)+1.96*sqrt(greatest(0,coalesce(variance(r.stress_net_bps),0))/nullif(count(*),0)) AS stress_ci95_high,
    CASE WHEN r.bucket='overall' THEN (SELECT count(*)::bigint FROM week_stats WHERE week_net>0) ELSE 0::bigint END AS positive_weeks,
    CASE WHEN r.bucket='overall' THEN (SELECT count(*)::bigint FROM week_stats) ELSE 0::bigint END AS total_weeks,
    CASE WHEN r.bucket='overall' THEN coalesce((SELECT max(positive_contribution)/nullif((SELECT sum(positive_contribution) FROM week_stats),0) FROM week_stats),0) ELSE 0 END AS max_positive_week_share,
    (SELECT p90 FROM thresholds) AS threshold_p90,(SELECT p10 FROM thresholds) AS threshold_p10,
    min(r.entry_ms)::bigint AS first_entry_ms,max(r.entry_ms)::bigint AS last_entry_ms
  FROM rows r GROUP BY r.bucket,r.direction
)
SELECT * FROM stats
ORDER BY CASE WHEN bucket='overall' THEN 0 WHEN bucket='direction' THEN 2 ELSE 1 END,bucket,direction;
$function$;

REVOKE ALL ON FUNCTION public.research_hvol1_readiness(bigint,bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hvol1_readiness(bigint,bigint) TO anon, authenticated, service_role;
REVOKE ALL ON FUNCTION public.research_hvol1_scan_frozen(bigint,bigint,numeric,numeric,numeric) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hvol1_scan_frozen(bigint,bigint,numeric,numeric,numeric) TO anon, authenticated, service_role;
