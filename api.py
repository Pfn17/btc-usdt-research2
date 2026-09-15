from __future__ import annotations

from fastapi import Query
from btc_research.api import app
from btc_research import ohlcv_dashboard  # noqa: F401

OOS_START_MS = 1785110400000
OOS_END_MS = 1788739140000


def _overall(rows):
    return next((r for r in rows if str(r.get("bucket", "")).lower() == "overall"), rows[0] if rows else None)


async def _run_catalog_item(key: str):
    live = app.state.live
    try:
        if key == "D_OHLCV_MOM_4H_4H":
            rows = await live.db.rpc("research_ohlcv_momentum_frozen", {
                "p_as_of_open_time_ms": OOS_END_MS,
                "p_lookback_minutes": 240,
                "p_horizon_minutes": 240,
                "p_sample_limit": 20000,
                "p_fee_bps": 4,
                "p_slippage_bps": 1,
            })
            return {"run_state": "LIVE_DIAGNOSTIC", "result": _overall(rows), "rows": rows, "boundary": "owner OOS end used as evaluation cutoff; historical family definition predates the frozen OOS registry"}
        if key == "H_FB1_FUNDING_SIGN_4H":
            rows = await live.hfb1_scan(OOS_START_MS, OOS_END_MS, 4, 1)
            return {"run_state": "LIVE_OOS", "result": _overall(rows), "rows": rows, "boundary": "owner-frozen OOS 2026-07-27 00:00 UTC through 2026-09-06 23:59 UTC"}
        if key == "H-FB3":
            result = await live.hfb3_result()
            return {"run_state": "LIVE_PERSISTED_RESULT", "result": _overall(result.get("data", []) if result else []), "rows": result.get("data", []) if result else [], "evidence": result.get("evidence") if result else None, "boundary": "persisted production research result; six complete OOS ISO weeks are represented in the evidence"}
        if key == "H-MR1":
            rows = await live.hmr1_scan(OOS_START_MS, OOS_END_MS, 4, 1, 12)
            return {"run_state": "LIVE_OOS", "result": _overall(rows), "rows": rows, "boundary": "owner-frozen OOS 2026-07-27 00:00 UTC through 2026-09-06 23:59 UTC; candidate windows overlapping recorded contamination are excluded"}
        if key == "H-SW1":
            rows = await live.sw1_claude_scan(OOS_END_MS, 4, 1, 3)
            return {"run_state": "LIVE_OOS_REFERENCE", "result": _overall(rows), "rows": rows, "boundary": "evaluation cutoff frozen at owner OOS end; reference method remains independently unverified"}
        if key == "H-VOL1":
            wrapped = await live.db.rpc("research_hvol1_scan_public", {"p_oos_start_ms": OOS_START_MS, "p_as_of_ms": OOS_END_MS, "p_fee_bps": 4, "p_slippage_bps": 1, "p_stress_round_trip_bps": 12})
            rows = (wrapped[0] or {}).get("payload", []) if wrapped else []
            return {"run_state": "LIVE_OOS", "result": _overall(rows), "rows": rows, "boundary": "owner-frozen OOS; train-only P90/P10; exact 120-minute predecessor and exact +120-minute exit; contamination window excluded at candidate-window level"}
        if key == "HC2_CONDITIONAL_STATE":
            feature = await live.latest_feature()
            if not feature:
                return {"run_state": "BLOCKED_NO_LIVE_FEATURE_DATA", "result": None, "rows": [], "boundary": "live microstructure feature store has no current row; no result is fabricated"}
            rows = await live.conditional_alpha_scan(int(feature["event_time_ms"]), 60, 50000, 60, 60, 4, 1)
            return {"run_state": "LIVE_DIAGNOSTIC", "result": _overall(rows), "rows": rows, "boundary": "latest live feature cutoff; not the owner-frozen OOS gate"}
        if key == "HC2_OHLCV_MOMENTUM_CONDITIONAL":
            rows = await live.db.rpc("research_ohlcv_momentum_frozen", {"p_as_of_open_time_ms": OOS_END_MS, "p_lookback_minutes": 15, "p_horizon_minutes": 1, "p_sample_limit": 20000, "p_fee_bps": 4, "p_slippage_bps": 1})
            return {"run_state": "LIVE_DIAGNOSTIC", "result": _overall(rows), "rows": rows, "boundary": "OHLCV-only diagnostic at frozen OOS cutoff; this is not the microstructure-conditioned HC2 path"}
    except Exception as exc:
        return {"run_state": "LIVE_ERROR", "result": None, "rows": [], "error": str(exc), "boundary": "backend error surfaced verbatim as state; no synthetic result"}
    return {"run_state": "REGISTRY_ONLY", "result": None, "rows": [], "boundary": "no live execution surface registered"}


@app.get("/api/v1/research/hvol1-live")
async def research_hvol1_live(oos_start_ms: int = Query(OOS_START_MS, ge=0), as_of_ms: int = Query(OOS_END_MS, ge=0)):
    wrapped = await app.state.live.db.rpc("research_hvol1_scan_public", {"p_oos_start_ms": oos_start_ms, "p_as_of_ms": as_of_ms, "p_fee_bps": 4, "p_slippage_bps": 1, "p_stress_round_trip_bps": 12})
    rows = (wrapped[0] or {}).get("payload", []) if wrapped else []
    return {"status": "RESEARCH_ONLY", "method": "H-VOL1", "data": rows, "parameters": {"oos_start_ms": oos_start_ms, "as_of_ms": as_of_ms, "fee_bps_per_side": 4, "slippage_bps_per_side": 1, "stress_round_trip_bps": 12, "horizon_minutes": 120}, "trading_enabled": False, "research_status": "frozen_scan_unverified", "authorization": "NOT GRANTED"}


@app.get("/api/v1/research/catalog")
async def research_catalog():
    live = app.state.live
    hypotheses = await live.db.select("research_hypotheses", "select=id,hypothesis_key,family_id,statement,direction,horizon_seconds,target_definition,feature_set,created_at,frozen_at&order=hypothesis_key.asc")
    decisions = await live.db.select("owner_decisions", "select=id,decision_type,title,decision,owner_reason,scope,related_hypothesis,status,effective_at,recorded_by&status=eq.ACTIVE&order=effective_at.desc")
    contamination = await live.db.select("contamination_intervals", "select=id,started_at,ended_at,reason,created_at&order=started_at.asc")
    health = await live.latest_health()
    session = await live.current_session()
    latest = await live.latest_ohlcv(1)
    results = {}
    for h in hypotheses:
        results[h["hypothesis_key"]] = await _run_catalog_item(h["hypothesis_key"])
    return {"status": "LIVE", "symbol": "BTCUSDT", "generated_at_ms": int(__import__("time").time() * 1000), "oos_boundary": {"start_ms": OOS_START_MS, "end_ms": OOS_END_MS, "status": "OWNER_FROZEN"}, "hypotheses": hypotheses, "results": results, "owner_decisions": decisions, "contamination": contamination, "collector_health": health, "running_session": session, "latest_ohlcv": latest[0] if latest else None, "execution": {"trading_enabled": False, "authorization": "NOT GRANTED"}}


__all__ = ["app"]
