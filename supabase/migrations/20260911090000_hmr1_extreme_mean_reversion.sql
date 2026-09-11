-- H-MR1: intraday extreme-candle mean reversion.
-- Frozen, read-only research function. It does not place orders or promote results.
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
WITH params AS (
  SELECT p_oos_start_ms::bigint AS oos_start_ms,
         p_as_of_ms::bigint AS as_of_ms,
         greatest(0,p_fee_bps)::numeric AS fee_bps,
         greatest(0,p_slippage_bps)::numeric AS slippage_bps,
         greatest(0,p_stress_round_trip_bps)::numeric AS stress_rt_bps
),
ordered AS (
  SELECT o.open_time_ms, o.open, o.close,
         lag(o.close,15) OVER (ORDER BY o.open_time_ms) AS close_15m_ago
  FROM ohlcv_1m o CROSS JOIN params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND o.open_time_ms <= p.as_of_ms
),
returns AS (
  SELECT x.*,
         10000.0*(x.close/x.close_15m_ago-1.0) AS return_15m_bps
  FROM ordered x
  WHERE x.close_15m_ago IS NOT NULL AND x.close_15m_ago > 0
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
  WHERE r.open_time_ms < p.as_of_ms
    AND r.open_time_ms >= p.oos_start_ms
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
nonoverlap AS (
  SELECT z.*
  FROM (
    SELECT f.*, lag(f.exit_ms) OVER (ORDER BY f.entry_ms) AS previous_exit_ms
    FROM with_fills f
  ) z
  WHERE z.previous_exit_ms IS NULL OR z.entry_ms >= z.previous_exit_ms
),
scored AS (
  SELECT n.*,
         10000.0 * (CASE WHEN n.direction='LONG' THEN 1 ELSE -1 END)
           * (n.exit_price-n.entry_price)/NULLIF(n.entry_price,0) AS gross_bps
  FROM nonoverlap n
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
  SELECT 'overall'::text AS bucket, 'ALL'::text AS direction, n.* FROM net n
  UNION ALL
  SELECT 'week_'||iso_year||'_W'||lpad(iso_week::text,2,'0'), 'ALL', n.* FROM net n
  UNION ALL
  SELECT 'direction'::text, n.direction, n.* FROM net n
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
         CASE WHEN r.bucket='overall' THEN (
           SELECT count(*)::bigint FROM (
             SELECT iso_year,iso_week FROM net GROUP BY iso_year,iso_week HAVING avg(net_bps)>0
           ) pw
         ) ELSE 0::bigint END AS positive_weeks,
         CASE WHEN r.bucket='overall' THEN (
           SELECT count(*)::bigint FROM (SELECT iso_year,iso_week FROM net GROUP BY iso_year,iso_week) tw
         ) ELSE 0::bigint END AS total_weeks,
         min(r.entry_ms)::bigint AS first_entry_ms,
         max(r.entry_ms)::bigint AS last_entry_ms
  FROM rows r GROUP BY r.bucket,r.direction
)
SELECT * FROM stats
ORDER BY CASE WHEN bucket='overall' THEN 0 WHEN bucket='direction' THEN 2 ELSE 1 END,bucket,direction;
$function$;

REVOKE ALL ON FUNCTION public.research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_hmr1_scan_frozen(bigint,bigint,numeric,numeric,numeric) TO anon, authenticated, service_role;
