from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def handler(request):
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    if not url or not key:
        return {"statusCode": 500, "headers": {"content-type": "application/json"}, "body": json.dumps({"error": "Supabase configuration unavailable"})}

    q = getattr(request, "query", {}) or {}
    try:
        as_of = int(q.get("as_of_open_time_ms")) if q.get("as_of_open_time_ms") else None
        lookback = min(max(int(q.get("lookback_minutes", 720)), 30), 10080)
        horizon = int(q.get("horizon_minutes", 60))
        if horizon not in (5, 15, 30, 60, 120, 240):
            raise ValueError("horizon_minutes must be one of 5,15,30,60,120,240")
        sample = min(max(int(q.get("sample_limit", 50000)), 5000), 200000)
        fee = float(q.get("fee_bps", 4))
        slip = float(q.get("slippage_bps", 0))
    except (TypeError, ValueError) as exc:
        return {"statusCode": 400, "headers": {"content-type": "application/json"}, "body": json.dumps({"error": str(exc)})}

    if as_of is None:
        # Query the latest 1m candle first.
        params = urlencode({"select": "open_time_ms", "symbol": "eq.BTCUSDT", "interval": "eq.1m", "order": "open_time_ms.desc", "limit": 1})
        req = Request(f"{url}/rest/v1/ohlcv_1m?{params}", headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urlopen(req, timeout=10) as response:
            rows = json.loads(response.read().decode())
        if not rows:
            return {"statusCode": 503, "headers": {"content-type": "application/json"}, "body": json.dumps({"error": "No OHLCV data"})}
        as_of = int(rows[0]["open_time_ms"])

    payload = json.dumps({
        "p_as_of_open_time_ms": as_of,
        "p_lookback_minutes": lookback,
        "p_horizon_minutes": horizon,
        "p_sample_limit": sample,
        "p_fee_bps": fee,
        "p_slippage_bps": slip,
    }).encode()
    req = Request(f"{url}/rest/v1/rpc/research_ohlcv_momentum_frozen", data=payload, method="POST", headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
    except Exception as exc:
        return {"statusCode": 503, "headers": {"content-type": "application/json"}, "body": json.dumps({"error": "OHLCV research unavailable", "detail": str(exc)})}

    row = result[0] if result else None
    return {"statusCode": 200, "headers": {"content-type": "application/json", "cache-control": "no-store"}, "body": json.dumps({"method": "OHLCV_MOMENTUM_FROZEN", "as_of_open_time_ms": as_of, "parameters": {"lookback_minutes": lookback, "horizon_minutes": horizon, "sample_limit": sample, "fee_bps_per_side": fee, "slippage_bps_per_side": slip}, "result": row, "live_trading_enabled": False})}
