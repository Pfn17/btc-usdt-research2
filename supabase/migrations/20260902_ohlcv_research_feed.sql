-- Lightweight Binance 1-minute OHLCV research feed.
-- Public market data only; no trading credentials are used.
CREATE TABLE IF NOT EXISTS public.ohlcv_1m (
  symbol text NOT NULL,
  interval text NOT NULL DEFAULT '1m',
  open_time_ms bigint NOT NULL,
  close_time_ms bigint NOT NULL,
  open numeric NOT NULL,
  high numeric NOT NULL,
  low numeric NOT NULL,
  close numeric NOT NULL,
  volume numeric NOT NULL,
  quote_volume numeric NOT NULL,
  trade_count bigint NOT NULL,
  taker_buy_volume numeric NOT NULL,
  taker_buy_quote_volume numeric NOT NULL,
  collected_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (symbol, interval, open_time_ms),
  CHECK (interval = '1m'),
  CHECK (open > 0 AND high > 0 AND low > 0 AND close > 0),
  CHECK (high >= low),
  CHECK (volume >= 0 AND quote_volume >= 0 AND trade_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_1m_symbol_time
  ON public.ohlcv_1m (symbol, open_time_ms DESC);

ALTER TABLE public.ohlcv_1m ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS ohlcv_1m_public_read ON public.ohlcv_1m;
CREATE POLICY ohlcv_1m_public_read ON public.ohlcv_1m
  FOR SELECT USING (true);

CREATE OR REPLACE FUNCTION public.research_ohlcv_momentum_frozen(
  p_as_of_open_time_ms bigint,
  p_lookback_minutes integer DEFAULT 60,
  p_horizon_minutes integer DEFAULT 15,
  p_sample_limit integer DEFAULT 20000,
  p_fee_bps numeric DEFAULT 4,
  p_slippage_bps numeric DEFAULT 0
)
RETURNS TABLE(
  n bigint,
  mean_gross_bps numeric,
  mean_net_bps numeric,
  win_rate numeric,
  ci95_low numeric,
  ci95_high numeric
)
LANGUAGE sql STABLE AS $function$
WITH params AS (
  SELECT greatest(1,p_lookback_minutes)::bigint * 60000 AS lookback_ms,
         greatest(1,p_horizon_minutes)::bigint * 60000 AS horizon_ms,
         greatest(1000,least(p_sample_limit,100000)) AS sample_limit
),
entries AS (
  SELECT o.*
  FROM public.ohlcv_1m o, params p
  WHERE o.symbol='BTCUSDT' AND o.interval='1m'
    AND o.open_time_ms <= p_as_of_open_time_ms
  ORDER BY o.open_time_ms DESC
  LIMIT (SELECT sample_limit FROM params)
),
obs AS (
  SELECT e.open_time_ms,e.close,e.volume,
         prior.close AS prior_close,
         future.close AS future_close
  FROM entries e, params p
  LEFT JOIN LATERAL (
    SELECT x.close FROM public.ohlcv_1m x
    WHERE x.symbol=e.symbol AND x.interval='1m'
      AND x.open_time_ms = e.open_time_ms-p.lookback_ms
  ) prior ON true
  LEFT JOIN LATERAL (
    SELECT x.close FROM public.ohlcv_1m x
    WHERE x.symbol=e.symbol AND x.interval='1m'
      AND x.open_time_ms = e.open_time_ms+p.horizon_ms
  ) future ON true
),
scored AS (
  SELECT *,
    10000.0*(close-prior_close)/prior_close AS lookback_bps,
    10000.0*(future_close-close)/close AS forward_bps
  FROM obs
  WHERE prior_close IS NOT NULL AND future_close IS NOT NULL AND prior_close > 0
),
raw AS (
  SELECT *,
    sign(lookback_bps)*forward_bps AS gross_bps,
    sign(lookback_bps)*forward_bps-(2*p_fee_bps+2*p_slippage_bps) AS net_bps
  FROM scored
  WHERE lookback_bps <> 0
),
stats AS (
  SELECT count(*) n, avg(gross_bps) mean_gross_bps, avg(net_bps) mean_net_bps,
         avg((net_bps>0)::int)::numeric win_rate,
         avg(gross_bps)-1.96*sqrt(greatest(0,coalesce(variance(gross_bps),0))/nullif(count(*),0)) ci95_low,
         avg(gross_bps)+1.96*sqrt(greatest(0,coalesce(variance(gross_bps),0))/nullif(count(*),0)) ci95_high
  FROM raw
)
SELECT * FROM stats;
$function$;
