-- H-MR1 gate correction: exact 15-minute predecessor, chronological greedy non-overlap,
-- and read-only data-readiness facts. No scan is invoked by this migration.

CREATE OR REPLACE FUNCTION public.research_hmr1_scan_frozen(
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
  first_entry_ms bigint,
  last_entry_ms bigint
)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
AS $function$
WITH RECURSIVE params AS (
  SELECT p_oos_start_ms::bigint AS oos_start_ms,
         p_as_of_ms::bigint AS as_of_ms,
         greatest(0,p_fee_bps)::numeric AS fee_bps,
         greatest(0,p_slippage_bps)::numeric AS slippage_bps,
         greatest(0,p_stress_round_trip_bps)::numeric AS stress_rt_bps
),
-- A predecessor is valid only when the exact t-15 minute candle exists.
exact_predecessors AS (
  SELECT o.open_time_ms, o.open, o.close, prev.close AS close_15m_ago
  FROM ohlcv_1m o
  JOIN ohlcv_1m prev
    ON prev.symbol=o.symbol AND prev.interval=o.interval
   AND prev.open_time_ms=o.open_time_ms-15*60*1000
  CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND o.open_time_ms <= p.as_of_ms
),
returns AS (
  SELECT x.*, 10000.0*(x.close/x.close_15m_ago-1.0) AS return_15m_bps
  FROM exact_predecessors x
  WHERE x.close_15m_ago > 0
),
train_threshold AS (
  SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY abs(r.return_15m_bps)) AS threshold_bps
  FROM returns r CROSS JOIN params p
  WHERE r.open_time_ms < p.oos_start_ms
),
raw_candidates AS (
  SELECT r.open_time_ms AS trigger_ms,
         CASE WHEN r.return_15m_bps > 0 THEN 'SHORT' ELSE 'LONG' END AS direction
  FROM returns r CROSS JOIN params p CROSS JOIN train_threshold t
  WHERE p.oos_start_ms IS NOT NULL
    AND r.open_time_ms >= p.oos_start_ms
    AND r.open_time_ms < p.as_of_ms
    AND t.threshold_bps IS NOT NULL
    AND abs(r.return_15m_bps) >= t.threshold_bps
),
with_fills AS (
  SELECT c.trigger_ms, c.direction, e.entry_ms, e.entry_price, x.exit_ms, x.exit_price
  FROM raw_candidates c
  JOIN LATERAL (
    SELECT o.open_time_ms AS entry_ms, o.open AS entry_price
    FROM ohlcv_1m o
    WHERE o.symbol='BTCUSDT' AND o.interval='1m'
      AND o.open_time_ms >= c.trigger_ms + 60000
      AND o.open_time_ms <= c.trigger_ms + 3600000
    ORDER BY o.open_time_ms LIMIT 1
  ) e ON true
  JOIN LATERAL (
    SELECT o.open_time_ms AS exit_ms, o.close AS exit_price
    FROM ohlcv_1m o
    WHERE o.symbol='BTCUSDT' AND o.interval='1m'
      AND o.open_time_ms >= e.entry_ms + 3600000
      AND o.open_time_ms <= e.entry_ms + 7200000
    ORDER BY o.open_time_ms LIMIT 1
  ) x ON true
),
-- Greedy chronological selection: accept the first valid candidate, then the
-- first candidate whose entry is at/after the accepted trade's scheduled exit.
ordered_fills AS (
  SELECT f.*, row_number() OVER (ORDER BY f.entry_ms, f.trigger_ms) AS candidate_no
  FROM with_fills f
),
greedy AS (
  SELECT f.*
  FROM ordered_fills f
  WHERE f.candidate_no=1
  UNION ALL
  SELECT next_f.*
  FROM greedy accepted
  CROSS JOIN LATERAL (
    SELECT f.*
    FROM ordered_fills f
    WHERE f.entry_ms >= accepted.exit_ms
    ORDER BY f.entry_ms, f.trigger_ms
    LIMIT 1
  ) next_f
),
scored AS (
  SELECT g.*,
         10000.0 * (CASE WHEN g.direction='LONG' THEN 1 ELSE -1 END)
           * (g.exit_price-g.entry_price)/NULLIF(g.entry_price,0) AS gross_bps
  FROM greedy g
),
net AS (
  SELECT s.*,
         s.gross_bps - 2*(p.fee_bps+p.slippage_bps) AS net_bps,
         s.gross_bps - p.stress_rt_bps AS stress_net_bps,
         extract(isoyear FROM to_timestamp(s.entry_ms/1000.0))::int AS iso_year,
         extract(week FROM to_timestamp(s.entry_ms/1000.0))::int AS iso_week
  FROM scored s CROSS JOIN params p
),
rows AS (
  SELECT 'overall'::text AS bucket, 'ALL'::text AS direction, n.trigger_ms, n.entry_ms, n.entry_price, n.exit_ms, n.exit_price, n.gross_bps, n.net_bps, n.stress_net_bps, n.iso_year, n.iso_week FROM net n
  UNION ALL
  SELECT 'week_'||iso_year||'_W'||lpad(iso_week::text,2,'0'), 'ALL', n.trigger_ms, n.entry_ms, n.entry_price, n.exit_ms, n.exit_price, n.gross_bps, n.net_bps, n.stress_net_bps, n.iso_year, n.iso_week FROM net n
  UNION ALL
  SELECT 'direction'::text, n.direction, n.trigger_ms, n.entry_ms, n.entry_price, n.exit_ms, n.exit_price, n.gross_bps, n.net_bps, n.stress_net_bps, n.iso_year, n.iso_week FROM net n
),
stats AS (
  SELECT r.bucket, r.direction, count(*)::bigint AS n,
         avg(r.gross_bps) AS mean_gross_bps,
         avg(r.net_bps) AS mean_net_bps,
         avg(r.stress_net_bps) AS mean_stress_net_bps,
         avg((r.net_bps>0)::int)::numeric AS win_rate,
         avg(r.net_bps)-1.96*sqrt(greatest(0,coalesce(variance(r.net_bps),0))/nullif(count(*),0)) AS net_ci95_low,
         avg(r.net_bps)+1.96*sqrt(greatest(0,coalesce(variance(r.net_bps),0))/nullif(count(*),0)) AS net_ci95_high,
         avg(r.stress_net_bps)-1.96*sqrt(greatest(0,coalesce(variance(r.stress_net_bps),0))/nullif(count(*),0)) AS stress_ci95_low,
         avg(r.stress_net_bps)+1.96*sqrt(greatest(0,coalesce(variance(r.stress_net_bps),0))/nullif(count(*),0)) AS stress_ci95_high,
         CASE WHEN r.bucket='overall' THEN (SELECT count(*)::bigint FROM (SELECT iso_year,iso_week FROM net GROUP BY iso_year,iso_week HAVING avg(net_bps)>0) pw) ELSE 0::bigint END AS positive_weeks,
         CASE WHEN r.bucket='overall' THEN (SELECT count(*)::bigint FROM (SELECT iso_year,iso_week FROM net GROUP BY iso_year,iso_week) tw) ELSE 0::bigint END AS total_weeks,
         min(r.entry_ms)::bigint AS first_entry_ms,
         max(r.entry_ms)::bigint AS last_entry_ms
  FROM rows r GROUP BY r.bucket,r.direction
)
SELECT * FROM stats
ORDER BY CASE WHEN bucket='overall' THEN 0 WHEN bucket='direction' THEN 2 ELSE 1 END,bucket,direction;
$function$;

CREATE OR REPLACE FUNCTION public.research_hmr1_readiness(
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
  exact_predecessor_count bigint,
  exact_predecessor_rate numeric,
  entry_available_count bigint,
  exit_available_count bigint,
  training_candles bigint,
  oos_candles bigint,
  complete_iso_weeks bigint,
  oos_boundary_frozen boolean,
  outcome_run boolean
)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
AS $function$
WITH bounds AS (
  SELECT min(o.open_time_ms)::bigint AS start_ms, max(o.open_time_ms)::bigint AS end_ms,
         count(*)::bigint AS candles
  FROM ohlcv_1m o WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms <= p_as_of_ms
),
coverage AS (
  SELECT b.*, greatest(0, ((b.end_ms-b.start_ms)/60000)+1)::bigint AS expected
  FROM bounds b
),
exact AS (
  SELECT count(*)::bigint AS exact_count
  FROM ohlcv_1m o JOIN ohlcv_1m prev
    ON prev.symbol=o.symbol AND prev.interval=o.interval
   AND prev.open_time_ms=o.open_time_ms-15*60*1000
  WHERE o.symbol='BTCUSDT' AND o.interval='1m' AND o.open_time_ms <= p_as_of_ms
),
entry AS (
  SELECT count(*)::bigint AS available
  FROM ohlcv_1m o WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND o.open_time_ms >= COALESCE(p_oos_start_ms,p_as_of_ms+1)+60000
    AND o.open_time_ms <= p_as_of_ms
),
exit_data AS (
  SELECT count(*)::bigint AS available
  FROM ohlcv_1m o WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND o.open_time_ms >= COALESCE(p_oos_start_ms,p_as_of_ms+1)+3600000
    AND o.open_time_ms <= p_as_of_ms
),
oos_weeks AS (
  SELECT count(*)::bigint AS weeks
  FROM (SELECT extract(isoyear FROM to_timestamp(o.open_time_ms/1000.0))::int y, extract(week FROM to_timestamp(o.open_time_ms/1000.0))::int w
        FROM ohlcv_1m o WHERE o.symbol='BTCUSDT' AND o.interval='1m'
          AND p_oos_start_ms IS NOT NULL AND o.open_time_ms >= p_oos_start_ms AND o.open_time_ms <= p_as_of_ms
        GROUP BY 1,2 HAVING count(*) >= 7*24*60) q
),
status AS (
  SELECT c.*, e.exact_count, en.available entry_count, ex.available exit_count, ow.weeks,
         CASE WHEN p_oos_start_ms IS NOT NULL AND p_oos_start_ms < p_as_of_ms THEN true ELSE false END AS boundary_frozen
  FROM coverage c CROSS JOIN exact e CROSS JOIN entry en CROSS JOIN exit_data ex CROSS JOIN oos_weeks ow
)
SELECT 'H-MR1',
       CASE WHEN s.boundary_frozen AND s.expected=s.candles AND s.exact_count>=greatest(0,s.expected-15) AND s.entry_count>0 AND s.exit_count>0 AND s.weeks>=6 THEN 'DATA_READY_OOS_BOUNDARY_FROZEN' ELSE 'NOT_READY' END,
       p_as_of_ms, p_oos_start_ms, s.start_ms, s.end_ms, s.candles, s.expected,
       greatest(0,s.expected-s.candles), s.expected=s.candles,
       s.exact_count, round(s.exact_count::numeric/nullif(s.candles,0),6), s.entry_count, s.exit_count,
       CASE WHEN p_oos_start_ms IS NULL THEN 0 ELSE (SELECT count(*) FROM ohlcv_1m WHERE symbol='BTCUSDT' AND interval='1m' AND open_time_ms < p_oos_start_ms AND open_time_ms <= p_as_of_ms) END,
       CASE WHEN p_oos_start_ms IS NULL THEN 0 ELSE (SELECT count(*) FROM ohlcv_1m WHERE symbol='BTCUSDT' AND interval='1m' AND open_time_ms >= p_oos_start_ms AND open_time_ms <= p_as_of_ms) END,
       s.weeks, s.boundary_frozen, false
FROM status s;
$function$;

REVOKE ALL ON FUNCTION public.research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric) TO anon, authenticated, service_role;
REVOKE ALL ON FUNCTION public.research_hmr1_readiness(bigint,bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hmr1_readiness(bigint,bigint) TO anon, authenticated, service_role;
