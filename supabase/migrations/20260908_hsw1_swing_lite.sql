-- H-SW1: 24-hour swing-lite confirmation of prior price momentum and
-- the sign of the three most recent completed funding events.
-- This function is research-only. It is not an execution or promotion gate.
CREATE OR REPLACE FUNCTION public.research_sw1_scan_frozen(
  p_as_of_ms bigint,
  p_fee_bps numeric DEFAULT 4,
  p_slippage_bps numeric DEFAULT 1,
  p_funding_lookback integer DEFAULT 3
)
RETURNS TABLE(
  bucket text,
  n bigint,
  mean_gross_bps numeric,
  mean_net_bps numeric,
  win_rate numeric,
  net_ci95_low numeric,
  net_ci95_high numeric,
  first_entry_ms bigint,
  last_entry_ms bigint
)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
AS $function$
WITH params AS (
  SELECT 24::bigint * 60 * 60 * 1000 AS horizon_ms,
         greatest(0,p_fee_bps)::numeric AS fee_bps,
         greatest(0,p_slippage_bps)::numeric AS slippage_bps,
         3::integer AS lookback_events
),
-- One candidate per UTC day prevents overlapping 24-hour labels.
daily AS (
  SELECT DISTINCT ON ((o.open_time_ms / 86400000))
         o.open_time_ms, o.close, (o.open_time_ms / 86400000) AS day_key
  FROM ohlcv_1m o
  WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND o.open_time_ms <= p_as_of_ms
  ORDER BY (o.open_time_ms / 86400000), o.open_time_ms
),
candidates AS (
  SELECT d.open_time_ms AS entry_ms,
         d.close AS entry_price,
         f.close AS exit_price,
         10000.0 * (d.close-prior.close) / NULLIF(prior.close,0) AS momentum_bps
  FROM daily d
  CROSS JOIN params p
  JOIN LATERAL (
    SELECT x.close FROM ohlcv_1m x
    WHERE x.symbol='BTCUSDT' AND x.interval='1m'
      AND x.open_time_ms >= d.open_time_ms + p.horizon_ms
      AND x.open_time_ms <= d.open_time_ms + p.horizon_ms + 3600000
    ORDER BY x.open_time_ms LIMIT 1
  ) f ON true
  JOIN LATERAL (
    SELECT x.close FROM ohlcv_1m x
    WHERE x.symbol='BTCUSDT' AND x.interval='1m'
      AND x.open_time_ms >= d.open_time_ms - p.horizon_ms
      AND x.open_time_ms <= d.open_time_ms - p.horizon_ms + 3600000
    ORDER BY x.open_time_ms LIMIT 1
  ) prior ON true
),
with_funding AS (
  SELECT c.*, lf.rates,
         CASE WHEN c.momentum_bps > 0 AND lf.all_positive THEN 1
              WHEN c.momentum_bps < 0 AND lf.all_negative THEN -1
              ELSE 0 END AS direction
  FROM candidates c
  JOIN LATERAL (
    SELECT array_agg(e.funding_rate ORDER BY e.funding_time_ms DESC) AS rates,
           bool_and(e.funding_rate > 0) AS all_positive,
           bool_and(e.funding_rate < 0) AS all_negative
    FROM (
      SELECT e.funding_rate, e.funding_time_ms
      FROM funding_rate_events e
      WHERE e.symbol='BTCUSDT' AND e.funding_time_ms < c.entry_ms
      ORDER BY e.funding_time_ms DESC
      LIMIT 3
    ) e
  ) lf ON cardinality(lf.rates)=3
  GROUP BY c.entry_ms,c.entry_price,c.exit_price,c.momentum_bps,lf.rates,lf.all_positive,lf.all_negative
),
scored AS (
  SELECT w.entry_ms,
         10000.0 * w.direction * (w.exit_price-w.entry_price) / NULLIF(w.entry_price,0)
           + (-w.direction * 10000.0 * COALESCE((
               SELECT sum(e.funding_rate) FROM funding_rate_events e
               WHERE e.symbol='BTCUSDT' AND e.funding_time_ms > w.entry_ms
                 AND e.funding_time_ms <= w.entry_ms + p.horizon_ms
             ),0)) AS gross_bps,
         10000.0 * w.direction * (w.exit_price-w.entry_price) / NULLIF(w.entry_price,0)
           + (-w.direction * 10000.0 * COALESCE((
               SELECT sum(e.funding_rate) FROM funding_rate_events e
               WHERE e.symbol='BTCUSDT' AND e.funding_time_ms > w.entry_ms
                 AND e.funding_time_ms <= w.entry_ms + p.horizon_ms
             ),0))
           - 2*(p.fee_bps+p.slippage_bps) AS net_bps
  FROM with_funding w CROSS JOIN params p
  WHERE w.direction <> 0
),
rows AS (
  SELECT 'overall'::text AS bucket, s.* FROM scored s
  UNION ALL
  SELECT 'quarter_' || extract(year FROM to_timestamp(s.entry_ms/1000.0))::int || '_Q' || extract(quarter FROM to_timestamp(s.entry_ms/1000.0))::int, s.*
  FROM scored s
),
stats AS (
  SELECT r.bucket,count(*)::bigint AS n,avg(r.gross_bps) AS mean_gross_bps,
         avg(r.net_bps) AS mean_net_bps,avg((r.net_bps>0)::int)::numeric AS win_rate,
         avg(r.net_bps)-1.96*sqrt(greatest(0,coalesce(variance(r.net_bps),0))/nullif(count(*),0)) AS net_ci95_low,
         avg(r.net_bps)+1.96*sqrt(greatest(0,coalesce(variance(r.net_bps),0))/nullif(count(*),0)) AS net_ci95_high,
         min(r.entry_ms)::bigint AS first_entry_ms,max(r.entry_ms)::bigint AS last_entry_ms
  FROM rows r GROUP BY r.bucket
)
SELECT * FROM stats ORDER BY CASE WHEN bucket='overall' THEN 0 ELSE 1 END,bucket;
$function$;

REVOKE ALL ON FUNCTION public.research_sw1_scan_frozen(bigint,numeric,numeric,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.research_sw1_scan_frozen(bigint,numeric,numeric,integer) TO anon, authenticated, service_role;
