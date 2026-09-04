from __future__ import annotations

import asyncio
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, ORJSONResponse
from pydantic import BaseModel, ConfigDict


STALE_AFTER_MS = int(os.environ.get("BTC_API_STALE_AFTER_MS", "2000"))
WS_POLL_SECONDS = float(os.environ.get("BTC_API_WS_POLL_SECONDS", "1.0"))
DASHBOARD_PATH = Path(__file__).resolve().parents[2] / "dashboard" / "index.html"


class APIConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    url: str
    key: str
    symbol: str = "BTCUSDT"


def load_config() -> APIConfig:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_ANON_KEY", "") or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_PUBLISHABLE_KEY) are required")
    return APIConfig(url=url, key=key, symbol=os.environ.get("BTC_SYMBOL", "BTCUSDT").upper())


class SupabaseReadClient:
    def __init__(self, config: APIConfig) -> None:
        self.config = config
        self.client = httpx.AsyncClient(base_url=f"{config.url}/rest/v1", timeout=httpx.Timeout(15.0, connect=3.0), headers={"apikey": config.key, "Authorization": f"Bearer {config.key}"})

    async def close(self) -> None:
        await self.client.aclose()

    async def select(self, table: str, query: str) -> list[dict[str, Any]]:
        response = await self.client.get(f"/{table}?{query}")
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(f"unexpected {table} response")
        return payload

    async def rpc(self, function: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        response = await self.client.post(f"/rpc/{function}", json=payload)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise RuntimeError(f"unexpected {function} response")
        return data


class LiveAPI:
    def __init__(self, db: SupabaseReadClient) -> None:
        self.db = db

    async def latest_feature(self) -> dict[str, Any] | None:
        rows = await self.db.select("feature_snapshots", f"select=*&symbol=eq.{self.db.config.symbol}&order=event_time_ms.desc&limit=1")
        return rows[0] if rows else None

    async def latest_health(self) -> dict[str, Any] | None:
        rows = await self.db.select("collector_health", "select=*&order=updated_at.desc&limit=1")
        return rows[0] if rows else None

    async def current_session(self) -> dict[str, Any] | None:
        rows = await self.db.select("research_sessions", "select=id,symbol,mode,status,started_at,last_heartbeat_at,stopped_at&status=eq.running&order=last_heartbeat_at.desc&limit=1")
        return rows[0] if rows else None

    async def latest_ohlcv(self, limit: int = 3) -> list[dict[str, Any]]:
        return await self.db.select("ohlcv_1m", f"select=*&symbol=eq.{self.db.config.symbol}&interval=eq.1m&order=open_time_ms.desc&limit={max(1,min(limit,20))}")

    async def latest_funding_event(self) -> dict[str, Any] | None:
        rows = await self.db.select("funding_rate_events", f"select=*&symbol=eq.{self.db.config.symbol}&order=funding_time_ms.desc&limit=1")
        return rows[0] if rows else None

    async def funding_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return await self.db.select("funding_rate_events", f"select=*&symbol=eq.{self.db.config.symbol}&order=funding_time_ms.desc&limit={max(1,min(limit,200))}")

    async def signal_audit_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return await self.db.select("signal_audit_events", f"select=id,session_id,event_time_ms,observed_at,status,direction,source,rationale,gate_json,feature_json&source=eq.H-FB1&order=event_time_ms.desc&limit={max(1,min(limit,200))}")

    async def research_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for table in ("research_labels", "evaluations", "research_results", "research_hypotheses", "paper_signals"):
            rows = await self.db.select(table, "select=id&limit=1")
            counts[table] = len(rows)
        return counts

    async def edge_scan(self, horizon_seconds: int, fee_bps: float | None, sample_limit: int, as_of_event_time_ms: int | None) -> list[dict[str, Any]]:
        return await self.db.rpc("research_edge_scan_frozen", {"horizon_seconds": horizon_seconds, "fee_bps": fee_bps, "sample_limit": sample_limit, "as_of_event_time_ms": as_of_event_time_ms})

    async def wfo_scan(self, as_of_event_time_ms: int, horizon_seconds: int, sample_limit: int, purge_seconds: int, embargo_seconds: int, fee_bps: float, slippage_bps: float) -> list[dict[str, Any]]:
        return await self.db.rpc("research_wfo_signal_scan", {"p_as_of_event_time_ms": as_of_event_time_ms, "p_horizon_seconds": horizon_seconds, "p_sample_limit": sample_limit, "p_purge_seconds": purge_seconds, "p_embargo_seconds": embargo_seconds, "p_fee_bps": fee_bps, "p_slippage_bps": slippage_bps})

    async def conditional_alpha_scan(self, as_of_event_time_ms: int, horizon_seconds: int, sample_limit: int, purge_seconds: int, embargo_seconds: int, fee_bps: float, slippage_bps: float) -> list[dict[str, Any]]:
        return await self.db.rpc("research_conditional_alpha_scan", {"p_as_of_event_time_ms": as_of_event_time_ms, "p_horizon_seconds": horizon_seconds, "p_sample_limit": sample_limit, "p_purge_seconds": purge_seconds, "p_embargo_seconds": embargo_seconds, "p_fee_bps": fee_bps, "p_slippage_bps": slippage_bps})

    async def hfb1_scan(self, oos_start_ms: int, as_of_event_time_ms: int, fee_bps: float = 4.0, slippage_bps: float = 1.0) -> list[dict[str, Any]]:
        return await self.db.rpc("research_funding_hfb1", {"p_oos_start_ms": oos_start_ms, "p_as_of_event_time_ms": as_of_event_time_ms, "p_fee_bps": fee_bps, "p_slippage_bps": slippage_bps})

    async def live_imbalance_signal(self, sample_limit: int) -> list[dict[str, Any]]:
        return await self.db.rpc("research_live_imbalance_signal", {"p_sample_limit": sample_limit})


def freshness(row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {"available": False, "stale": True, "age_ms": None}
    value = row.get("receive_time_ns")
    if value is not None:
        age_ms = max(0, time.time_ns() // 1_000_000 - int(value) // 1_000_000)
    else:
        timestamp = row.get("updated_at") or row.get("created_at") or row.get("collected_at") or row.get("observed_at")
        if not timestamp:
            return {"available": True, "stale": True, "age_ms": None}
        parsed = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        age_ms = max(0, int((datetime.now(timezone.utc) - parsed).total_seconds() * 1000))
    return {"available": True, "stale": age_ms > STALE_AFTER_MS, "age_ms": age_ms}


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    db = SupabaseReadClient(config)
    app.state.live = LiveAPI(db)
    app.state.config = config
    try:
        yield
    finally:
        await db.close()


app = FastAPI(title="BTCUSDT Research API", version="0.6.0", default_response_class=ORJSONResponse, lifespan=lifespan)


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def dashboard() -> FileResponse:
    if not DASHBOARD_PATH.is_file():
        raise HTTPException(status_code=404, detail="dashboard unavailable")
    return FileResponse(DASHBOARD_PATH, media_type="text/html")


@app.get("/health")
async def health() -> dict[str, Any]:
    try:
        session = await app.state.live.current_session()
        feature = await app.state.live.latest_feature()
        feature_fresh = freshness(feature)
        return {"status": "ok" if session and feature_fresh["available"] and not feature_fresh["stale"] else "degraded", "symbol": app.state.config.symbol, "collector_session": session, "feature_freshness": feature_fresh}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="live data unavailable") from exc


@app.get("/api/v1/features/latest")
async def features_latest() -> dict[str, Any]:
    try:
        row = await app.state.live.latest_feature()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="feature store unavailable") from exc
    if row is None:
        raise HTTPException(status_code=503, detail="no live feature data")
    return {"data": row, "freshness": freshness(row)}


@app.get("/api/v1/collector/health")
async def collector_health() -> dict[str, Any]:
    try:
        row = await app.state.live.latest_health()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="collector health unavailable") from exc
    if row is None:
        raise HTTPException(status_code=503, detail="no collector health data")
    return {"data": row, "freshness": freshness(row)}


@app.get("/api/v1/session/current")
async def session_current() -> dict[str, Any]:
    try:
        row = await app.state.live.current_session()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="session store unavailable") from exc
    if row is None:
        raise HTTPException(status_code=503, detail="no running research session")
    return {"data": row, "freshness": freshness(row)}


@app.get("/api/v1/market/ohlcv/latest")
async def market_ohlcv_latest(limit: int = Query(3, ge=1, le=20)) -> dict[str, Any]:
    try:
        rows = await app.state.live.latest_ohlcv(limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="OHLCV store unavailable") from exc
    return {"data": rows, "freshness": freshness(rows[0] if rows else None)}


@app.get("/api/v1/funding/latest")
async def funding_latest() -> dict[str, Any]:
    try:
        row = await app.state.live.latest_funding_event()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="funding event store unavailable") from exc
    return {"data": row, "freshness": freshness(row)}


@app.get("/api/v1/signals/log")
async def signals_log(limit: int = Query(50, ge=1, le=200)) -> dict[str, Any]:
    try:
        rows = await app.state.live.signal_audit_events(limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="signal audit unavailable") from exc
    return {"data": rows, "count": len(rows), "source": "H-FB1"}


@app.get("/api/v1/signal/hfb1/current")
async def hfb1_current() -> dict[str, Any]:
    try:
        event = await app.state.live.latest_funding_event()
        if not event:
            return {"status": "NO_DATA", "signal": "NONE", "trading_enabled": False}
        direction = "LONG" if float(event["funding_rate"]) > 0 else "SHORT" if float(event["funding_rate"]) < 0 else "NONE"
        funding_time_ms = int(event["funding_time_ms"])
        maturity_ms = funding_time_ms + 240 * 60 * 1000
        now_ms = int(time.time() * 1000)
        return {"status": "OBSERVED", "signal": direction, "funding_rate": event["funding_rate"], "funding_time_ms": funding_time_ms, "maturity_time_ms": maturity_ms, "matured": now_ms >= maturity_ms, "trading_enabled": False, "method": "H-FB1 funding-rate sign at completed funding event"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="H-FB1 live signal unavailable") from exc


@app.get("/api/v1/research/hfb1")
async def research_hfb1(oos_start_ms: int | None = Query(None, ge=0), fee_bps: float = Query(4.0, ge=0, le=100), slippage_bps: float = Query(1.0, ge=0, le=100)) -> dict[str, Any]:
    try:
        latest = await app.state.live.latest_funding_event()
        if not latest:
            return {"status": "NO_DATA", "data": [], "trading_enabled": False}
        as_of = int(latest["funding_time_ms"])
        start = oos_start_ms if oos_start_ms is not None else as_of - 90 * 86_400_000
        rows = await app.state.live.hfb1_scan(start, as_of, fee_bps, slippage_bps)
        return {"status": "RESEARCH_ONLY", "data": rows, "parameters": {"oos_start_ms": start, "as_of_event_time_ms": as_of, "fee_bps_per_side": fee_bps, "slippage_bps_per_side": slippage_bps, "horizon_minutes": 240}, "trading_enabled": False}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="H-FB1 research unavailable") from exc


@app.get("/api/v1/research/edge-scan")
async def research_edge_scan(horizon_seconds: int = Query(60, ge=60, le=300), fee_bps: float | None = Query(None, ge=0, le=100), sample_limit: int = Query(50000, ge=5000, le=200000), as_of_event_time_ms: int | None = Query(None, ge=0)) -> dict[str, Any]:
    if horizon_seconds not in (60, 120, 180, 300):
        raise HTTPException(status_code=400, detail="horizon_seconds must be one of 60, 120, 180, 300")
    try:
        rows = await app.state.live.edge_scan(horizon_seconds, fee_bps, sample_limit, as_of_event_time_ms)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="edge scan unavailable") from exc
    return {"data": rows, "method": {"status": "exploratory_screen_only"}, "parameters": {"horizon_seconds": horizon_seconds, "fee_bps": fee_bps, "sample_limit": sample_limit, "as_of_event_time_ms": as_of_event_time_ms}}


@app.get("/api/v1/research/wfo")
async def research_wfo(horizon_seconds: int = Query(60, ge=60, le=300), sample_limit: int = Query(50000, ge=20000, le=200000), fee_bps: float = Query(4.0, ge=0, le=100), slippage_bps: float = Query(0.0, ge=0, le=100), purge_seconds: int = Query(60, ge=0, le=300), embargo_seconds: int = Query(60, ge=0, le=300)) -> dict[str, Any]:
    if horizon_seconds not in (60, 120, 180, 300):
        raise HTTPException(status_code=400, detail="horizon_seconds must be one of 60, 120, 180, 300")
    latest = await app.state.live.latest_feature()
    if not latest:
        raise HTTPException(status_code=503, detail="no live feature data")
    cutoff = int(latest["event_time_ms"])
    try:
        folds = await app.state.live.wfo_scan(cutoff, horizon_seconds, sample_limit, purge_seconds, embargo_seconds, fee_bps, slippage_bps)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="WFO scan unavailable") from exc
    positive_folds = sum(1 for r in folds if float(r.get("combined_net_ev_bps", 0)) > 0 and float(r.get("ci95_low", 0)) > 0)
    gate = bool(folds) and positive_folds == len(folds) and sum(int(r.get("combined_n", 0)) for r in folds) >= 5000
    return {"status": "PAPER_CANDIDATE" if gate else "NO_SIGNAL", "gate": {"all_folds_positive_and_ci95": gate, "positive_folds": positive_folds, "folds": len(folds), "min_effective_samples": 5000}, "parameters": {"cutoff_event_time_ms": cutoff, "horizon_seconds": horizon_seconds, "sample_limit": sample_limit, "fee_bps_per_side": fee_bps, "slippage_bps_per_side": slippage_bps, "purge_seconds": purge_seconds, "embargo_seconds": embargo_seconds}, "folds": folds, "limitations": ["baseline imbalance_1 quantile rule only", "no block bootstrap/FDR in this gate yet", "no executable L2 impact model", "paper signal only; live trading remains disabled"]}


@app.get("/api/v1/research/conditional-alpha")
async def research_conditional_alpha(horizon_seconds: int = Query(60, ge=60, le=300), sample_limit: int = Query(50000, ge=20000, le=200000), fee_bps: float = Query(4.0, ge=0, le=100), slippage_bps: float = Query(0.0, ge=0, le=100), purge_seconds: int = Query(60, ge=0, le=300), embargo_seconds: int = Query(60, ge=0, le=300)) -> dict[str, Any]:
    if horizon_seconds not in (60, 120, 180, 300):
        raise HTTPException(status_code=400, detail="horizon_seconds must be one of 60, 120, 180, 300")
    latest = await app.state.live.latest_feature()
    if not latest:
        raise HTTPException(status_code=503, detail="no live feature data")
    cutoff = int(latest["event_time_ms"])
    try:
        rows = await app.state.live.conditional_alpha_scan(cutoff, horizon_seconds, sample_limit, purge_seconds, embargo_seconds, fee_bps, slippage_bps)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="conditional alpha scan unavailable") from exc
    return {"status": "RESEARCH_ONLY", "parameters": {"cutoff_event_time_ms": cutoff, "horizon_seconds": horizon_seconds, "sample_limit": sample_limit, "fee_bps_per_side": fee_bps, "slippage_bps_per_side": slippage_bps, "purge_seconds": purge_seconds, "embargo_seconds": embargo_seconds}, "hypotheses": ["imbalance_1 + microprice deviation agreement + low spread", "imbalance_1 + order-flow agreement + low spread"], "data": rows, "limitations": ["only two preregistered interaction hypotheses", "fill/execution probability is not observed", "no ML", "no walk-the-book simulation", "not a live-trading approval"]}


@app.get("/api/v1/signal/current")
async def current_signal(fee_bps: float = Query(4.0, ge=0, le=100), slippage_bps: float = Query(0.0, ge=0, le=100)) -> dict[str, Any]:
    try:
        candidate = (await app.state.live.live_imbalance_signal(50000) or [None])[0]
        latest = await app.state.live.latest_feature()
        if not candidate or not latest:
            return {"signal": "NONE", "reason": "no live feature data"}
        cutoff = int(latest["event_time_ms"])
        folds = await app.state.live.wfo_scan(cutoff, 60, 50000, 60, 60, fee_bps, slippage_bps)
        gate = bool(folds) and all(float(r.get("combined_net_ev_bps", 0)) > 0 and float(r.get("ci95_low", 0)) > 0 for r in folds)
        direction = candidate["candidate_direction"] if gate else "NONE"
        return {"signal": direction, "status": "PAPER_CANDIDATE" if direction != "NONE" else "NO_SIGNAL", "feature": {"imbalance_1": candidate["imbalance_1"], "q20": candidate["q20"], "q80": candidate["q80"], "event_time_ms": candidate["event_time_ms"]}, "cost": {"fee_bps_per_side": fee_bps, "slippage_bps_per_side": slippage_bps}, "gate": {"all_oos_folds_positive_ci95": gate, "folds": folds}, "trading_enabled": False}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="signal engine unavailable") from exc


@app.get("/api/v1/research/ohlcv-scan")
async def research_ohlcv_scan(lookback_minutes: int = Query(720, ge=5, le=1440), horizon_minutes: int = Query(15, ge=5, le=240), fee_bps: float = Query(4.0, ge=0, le=100), slippage_bps: float = Query(0.0, ge=0, le=100), sample_limit: int = Query(50000, ge=5000, le=200000)) -> dict[str, Any]:
    latest = await app.state.live.latest_ohlcv(1)
    if not latest:
        raise HTTPException(status_code=503, detail="no OHLCV data")
    rows = await app.state.live.db.rpc("research_ohlcv_scan", {"p_lookback_minutes": lookback_minutes, "p_horizon_minutes": horizon_minutes, "p_fee_bps": fee_bps, "p_slippage_bps": slippage_bps, "p_sample_limit": sample_limit})
    return {"data": rows, "status": "RESEARCH_ONLY"}


@app.websocket("/ws/features")
async def websocket_features(websocket: WebSocket) -> None:
    await websocket.accept()
    last_key: tuple[Any, Any] | None = None
    try:
        while True:
            try:
                row = await app.state.live.latest_feature()
            except Exception:
                await websocket.send_json({"type": "status", "status": "degraded", "reason": "feature_store_unavailable"})
                await asyncio.sleep(WS_POLL_SECONDS)
                continue
            if row is None:
                await websocket.send_json({"type": "status", "status": "no_data"})
            else:
                key = (row.get("event_time_ms"), row.get("book_update_id"))
                if key != last_key:
                    await websocket.send_json({"type": "feature", "data": row, "freshness": freshness(row)})
                    last_key = key
            await asyncio.sleep(WS_POLL_SECONDS)
    except (WebSocketDisconnect, asyncio.CancelledError):
        return