-- Frozen short-horizon return autocorrelation / crossover scan.
-- Preregistered horizons: 5, 15, 30, 60, 120 seconds.
-- Lookback is fixed at 5 seconds to keep the hypothesis surface bounded.
-- Direction is preregistered: reversal for <60s; momentum for >=60s.
-- Dataset is frozen by p_as_of_event_time_ms; all labels remain session-local.
-- This is a research diagnostic, not a live-trading signal.
CREATE OR REPLACE FUNCTION public.research_autocorr_scan_frozen(
  p_as_of_event_time_ms bigint,
  p_horizons_seconds integer[] DEFAULT ARRAY[5,15,30,60,120],
  p_lookback_seconds integer DEFAULT 5,
  p_sample_limit integer DEFAULT 50000,
  p_fee_bps numeric DEFAULT 4,
  p_slippage_bps numeric DEFAULT 0
)
RETURNS TABLE(
  horizon_seconds integer,
  direction_mode text,
  n bigint,
  mean_gross_bps numeric,
  mean_net_bps numeric,
  win_rate numeric,
  autocorr numeric,
  ci95_low numeric,
  ci95_high numeric,
  fisher_p_value numeric
)
LANGUAGE sql STABLE AS $function$
WITH params AS (
  SELECT greatest(1,p_lookback_seconds)*1000 lookback_ms,
         greatest(1000,least(p_sample_limit,100000)) sample_limit
),
horizons AS (
  SELECT DISTINCT greatest(1,x)::integer horizon_seconds
  FROM unnest(p_horizons_seconds) u(x) WHERE x>0
),
entries AS (
  SELECT s.id,s.session_id,s.event_time_ms,s.mid_price,s.spread_bps
  FROM public.feature_snapshots s,params p
  WHERE s.symbol='BTCUSDT' AND s.event_time_ms<=p_as_of_event_time_ms AND s.mid_price>0
  ORDER BY s.event_time_ms DESC,s.id DESC LIMIT (SELECT sample_limit FROM params)
),
observations AS (
  SELECT e.id,e.session_id,e.event_time_ms,e.mid_price,e.spread_bps,h.horizon_seconds,
         prior.mid_price prior_mid,prior.event_time_ms prior_time,
         future.mid_price future_mid,future.event_time_ms future_time
  FROM entries e CROSS JOIN horizons h
  LEFT JOIN LATERAL (
    SELECT x.mid_price,x.event_time_ms FROM public.feature_snapshots x
    WHERE x.symbol='BTCUSDT' AND x.session_id=e.session_id AND x.event_time_ms<e.event_time_ms
      AND x.event_time_ms>=e.event_time_ms-(SELECT lookback_ms FROM params)-3000 AND x.mid_price>0
    ORDER BY x.event_time_ms DESC,x.id DESC LIMIT 1
  ) prior ON true
  LEFT JOIN LATERAL (
    SELECT x.mid_price,x.event_time_ms FROM public.feature_snapshots x
    WHERE x.symbol='BTCUSDT' AND x.session_id=e.session_id
      AND x.event_time_ms>=e.event_time_ms+h.horizon_seconds*1000
      AND x.event_time_ms<=e.event_time_ms+h.horizon_seconds*1000+3000 AND x.mid_price>0
    ORDER BY x.event_time_ms,x.id LIMIT 1
  ) future ON true
),
valid AS (
 SELECT o.*,10000.0*(o.mid_price-o.prior_mid)/o.prior_mid lookback_ret_bps,10000.0*(o.future_mid-o.mid_price)/o.mid_price forward_ret_bps
 FROM observations o
 WHERE o.prior_mid IS NOT NULL AND o.future_mid IS NOT NULL
   AND o.prior_time>=o.event_time_ms-(SELECT lookback_ms FROM params)-3000
   AND o.future_time<=o.event_time_ms+o.horizon_seconds*1000+3000
),
scored AS (
 SELECT v.*,CASE WHEN v.horizon_seconds<60 THEN 'reversal' ELSE 'momentum' END::text direction_mode,
        CASE WHEN v.horizon_seconds<60 THEN -sign(v.lookback_ret_bps) ELSE sign(v.lookback_ret_bps) END direction
 FROM valid v WHERE v.lookback_ret_bps<>0
),
raw AS (
 SELECT s.*,s.direction*s.forward_ret_bps gross_bps,
        s.direction*s.forward_ret_bps-(2*p_fee_bps+coalesce(s.spread_bps,0)+2*p_slippage_bps) net_bps
 FROM scored s
),
stats AS (
 SELECT r.horizon_seconds,r.direction_mode,count(*) n,avg(r.gross_bps) mean_gross_bps,avg(r.net_bps) mean_net_bps,
        avg((r.net_bps>0)::int)::numeric win_rate,corr(r.lookback_ret_bps,r.forward_ret_bps) autocorr,
        avg(r.gross_bps)-1.96*sqrt(greatest(0,coalesce(variance(r.gross_bps),0))/nullif(count(*),0)) ci95_low,
        avg(r.gross_bps)+1.96*sqrt(greatest(0,coalesce(variance(r.gross_bps),0))/nullif(count(*),0)) ci95_high
 FROM raw r GROUP BY r.horizon_seconds,r.direction_mode
)
SELECT s.horizon_seconds,s.direction_mode,s.n,s.mean_gross_bps,s.mean_net_bps,s.win_rate,s.autocorr,s.ci95_low,s.ci95_high,
 CASE WHEN s.autocorr IS NULL OR abs(s.autocorr)>=0.999999 OR s.n<=3 THEN NULL
      ELSE erfc(abs(atanh(s.autocorr))*sqrt(greatest(1,s.n-3))/sqrt(2.0)) END fisher_p_value
FROM stats s ORDER BY s.horizon_seconds;
$function$;

-- Remove the earlier prototype overload so calls cannot become ambiguous.
DROP FUNCTION IF EXISTS public.research_autocorr_scan_frozen(bigint,integer[],integer,integer,integer,integer,numeric,numeric);
