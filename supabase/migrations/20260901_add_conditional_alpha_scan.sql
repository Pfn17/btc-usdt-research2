-- Conditional alpha discovery: two preregistered interaction hypotheses.
-- Train thresholds are computed strictly before test_start - purge - embargo.
-- OOS scoring is chronological and session-local for the forward label.
CREATE OR REPLACE FUNCTION public.research_conditional_alpha_scan(
  p_as_of_event_time_ms bigint,
  p_horizon_seconds integer DEFAULT 60,
  p_sample_limit integer DEFAULT 50000,
  p_purge_seconds integer DEFAULT 60,
  p_embargo_seconds integer DEFAULT 60,
  p_fee_bps numeric DEFAULT 4,
  p_slippage_bps numeric DEFAULT 0
)
RETURNS TABLE(hypothesis text, fold integer, test_n bigint, signal_n bigint, signal_rate numeric, net_ev_bps numeric, win_rate numeric, ci95_low numeric, ci95_high numeric, mean_spread_bps numeric, mean_gross_bps numeric)
LANGUAGE sql STABLE AS $function$
WITH params AS (SELECT greatest(1,p_horizon_seconds)*1000 horizon_ms,greatest(0,p_purge_seconds)*1000 purge_ms,greatest(0,p_embargo_seconds)*1000 embargo_ms),
entries AS (
 SELECT s.id,s.session_id,s.event_time_ms,s.mid_price,s.spread_bps,s.imbalance_1,s.microprice,s.order_flow_1s,
 CASE WHEN s.mid_price>0 AND s.microprice IS NOT NULL THEN 10000.0*(s.microprice-s.mid_price)/s.mid_price END microprice_dev_bps
 FROM public.feature_snapshots s,params p WHERE s.symbol='BTCUSDT' AND s.event_time_ms<=p_as_of_event_time_ms-p.horizon_ms-3000 AND s.mid_price>0 AND s.imbalance_1 IS NOT NULL
 ORDER BY s.event_time_ms DESC,s.id DESC LIMIT greatest(20000,least(p_sample_limit,200000))
),
labeled AS (
 SELECT e.*,f.mid_price future_mid,10000.0*(f.mid_price-e.mid_price)/e.mid_price ret_bps,ntile(5) OVER(ORDER BY e.event_time_ms,e.id) fold
 FROM entries e CROSS JOIN params p JOIN LATERAL (SELECT x.mid_price FROM public.feature_snapshots x WHERE x.symbol='BTCUSDT' AND x.session_id=e.session_id AND x.event_time_ms>=e.event_time_ms+p.horizon_ms AND x.event_time_ms<=e.event_time_ms+p.horizon_ms+3000 AND x.mid_price>0 ORDER BY x.event_time_ms,x.id LIMIT 1) f ON true
),
bounds AS (SELECT l.fold,min(l.event_time_ms) test_start,count(*) test_n FROM labeled l WHERE l.fold BETWEEN 2 AND 5 GROUP BY l.fold),
train_quantiles AS (
 SELECT b.fold,
 percentile_cont(.20) WITHIN GROUP(ORDER BY l.imbalance_1) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms) i20,
 percentile_cont(.80) WITHIN GROUP(ORDER BY l.imbalance_1) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms) i80,
 percentile_cont(.25) WITHIN GROUP(ORDER BY l.microprice_dev_bps) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms AND l.microprice_dev_bps IS NOT NULL) m25,
 percentile_cont(.75) WITHIN GROUP(ORDER BY l.microprice_dev_bps) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms AND l.microprice_dev_bps IS NOT NULL) m75,
 percentile_cont(.25) WITHIN GROUP(ORDER BY l.order_flow_1s) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms AND l.order_flow_1s IS NOT NULL) o25,
 percentile_cont(.75) WITHIN GROUP(ORDER BY l.order_flow_1s) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms AND l.order_flow_1s IS NOT NULL) o75,
 percentile_cont(.75) WITHIN GROUP(ORDER BY l.spread_bps) FILTER(WHERE l.event_time_ms<b.test_start-p.purge_ms-p.embargo_ms AND l.spread_bps IS NOT NULL) s75
 FROM bounds b CROSS JOIN params p CROSS JOIN labeled l GROUP BY b.fold,b.test_start,p.purge_ms,p.embargo_ms
),
scored AS (
 SELECT l.*,b.test_n,
 CASE WHEN l.imbalance_1>=q.i80 AND l.microprice_dev_bps>=q.m75 AND l.spread_bps<=q.s75 THEN 1 WHEN l.imbalance_1<=q.i20 AND l.microprice_dev_bps<=q.m25 AND l.spread_bps<=q.s75 THEN -1 ELSE 0 END d_imicro,
 CASE WHEN l.imbalance_1>=q.i80 AND l.order_flow_1s>=q.o75 AND l.spread_bps<=q.s75 THEN 1 WHEN l.imbalance_1<=q.i20 AND l.order_flow_1s<=q.o25 AND l.spread_bps<=q.s75 THEN -1 ELSE 0 END d_iflow
 FROM labeled l JOIN bounds b ON b.fold=l.fold JOIN train_quantiles q ON q.fold=l.fold
),
expanded AS (
 SELECT s.*,v.hypothesis,v.direction FROM scored s CROSS JOIN LATERAL(VALUES('imbalance_microprice_lowspread',s.d_imicro),('imbalance_orderflow_lowspread',s.d_iflow)) v(hypothesis,direction) WHERE v.direction<>0
),
sc AS (SELECT e.*,e.direction*e.ret_bps-(2*p_fee_bps+coalesce(e.spread_bps,0)+2*p_slippage_bps) net_bps FROM expanded e),
stats AS (
 SELECT sc.hypothesis,sc.fold,max(sc.test_n) test_n,count(*) signal_n,avg(sc.net_bps) net_ev_bps,avg((sc.net_bps>0)::int) win_rate,avg(sc.direction*sc.ret_bps) mean_gross_bps,avg(sc.spread_bps) mean_spread_bps,
 avg(sc.net_bps)-1.96*sqrt(greatest(0,coalesce(variance(sc.net_bps),0))/nullif(count(*),0)) ci95_low,
 avg(sc.net_bps)+1.96*sqrt(greatest(0,coalesce(variance(sc.net_bps),0))/nullif(count(*),0)) ci95_high
 FROM sc GROUP BY sc.hypothesis,sc.fold
)
SELECT st.hypothesis,st.fold,st.test_n,st.signal_n,(st.signal_n::numeric/nullif(st.test_n,0)),st.net_ev_bps,st.win_rate,st.ci95_low,st.ci95_high,st.mean_spread_bps,st.mean_gross_bps FROM stats st ORDER BY st.hypothesis,st.fold;
$function$;