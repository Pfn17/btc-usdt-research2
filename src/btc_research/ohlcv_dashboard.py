from __future__ import annotations

from typing import Any
from fastapi import HTTPException, Query

from .api import app


def _live():
    return app.state.live


@app.get("/api/v1/research/ohlcv-scan")
async def research_ohlcv_scan(
    lookback_minutes: int = Query(60, ge=5, le=1440),
    horizon_minutes: int = Query(15, ge=5, le=240),
    sample_limit: int = Query(20000, ge=1000, le=200000),
    fee_bps: float = Query(4.0, ge=0, le=100),
    slippage_bps: float = Query(0.0, ge=0, le=100),
) -> dict[str, Any]:
    latest = await _live().db.select(
        "ohlcv_1m",
        f"select=open_time_ms,close_time_ms,open,high,low,close,volume,quote_volume,trade_count,taker_buy_volume,collected_at&symbol=eq.{app.state.config.symbol}&interval=eq.1m&order=open_time_ms.desc&limit=1",
    )
    if not latest:
        raise HTTPException(status_code=503, detail="no live OHLCV data")
    cutoff = int(latest[0]["open_time_ms"])
    try:
        rows = await _live().db.rpc(
            "research_ohlcv_momentum_frozen",
            {
                "p_as_of_open_time_ms": cutoff,
                "p_lookback_minutes": lookback_minutes,
                "p_horizon_minutes": horizon_minutes,
                "p_sample_limit": sample_limit,
                "p_fee_bps": fee_bps,
                "p_slippage_bps": slippage_bps,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="OHLCV research scan unavailable") from exc
    candle = latest[0]
    return {
        "status": "RESEARCH_ONLY",
        "signal_family": "OHLCV",
        "timing_context": "L2 may be used for execution timing only; it is not a predictive signal family.",
        "parameters": {
            "lookback_minutes": lookback_minutes,
            "horizon_minutes": horizon_minutes,
            "sample_limit": sample_limit,
            "fee_bps_per_side": fee_bps,
            "slippage_bps_per_side": slippage_bps,
            "as_of_open_time_ms": cutoff,
        },
        "latest_candle": candle,
        "data": rows,
        "live_trading_enabled": False,
        "gate": "NO_SIGNAL until positive OOS net EV is independently validated",
    }


@app.get("/api/v1/market/ohlcv/latest")
async def latest_ohlcv() -> dict[str, Any]:
    rows = await _live().db.select(
        "ohlcv_1m",
        f"select=*&symbol=eq.{app.state.config.symbol}&interval=eq.1m&order=open_time_ms.desc&limit=30",
    )
    if not rows:
        raise HTTPException(status_code=503, detail="no live OHLCV data")
    return {"data": rows, "count": len(rows)}


# Importing this module registers the routes on the existing FastAPI app.
