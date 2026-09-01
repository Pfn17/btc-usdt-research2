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
        self.client = httpx.AsyncClient(
            base_url=f"{config.url}/rest/v1",
            timeout=httpx.Timeout(15.0, connect=3.0),
            headers={"apikey": config.key, "Authorization": f"Bearer {config.key}"},
        )

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
        rows = await self.db.select(
            "feature_snapshots",
            f"select=*&symbol=eq.{self.db.config.symbol}&order=event_time_ms.desc&limit=1",
        )
        return rows[0] if rows else None

    async def latest_health(self) -> dict[str, Any] | None:
        rows = await self.db.select("collector_health", "select=*&order=updated_at.desc&limit=1")
        return rows[0] if rows else None

    async def current_session(self) -> dict[str, Any] | None:
        rows = await self.db.select(
            "research_sessions",
            "select=id,symbol,mode,status,started_at,last_heartbeat_at,stopped_at&status=eq.running&order=last_heartbeat_at.desc&limit=1",
        )
        return rows[0] if rows else None

    async def research_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for table in ("research_labels", "evaluations", "research_results", "research_hypotheses", "paper_signals"):
            rows = await self.db.select(table, "select=id&limit=1")
            counts[table] = len(rows)
        return counts

    async def edge_scan(
        self,
        horizon_seconds: int,
        fee_bps: float | None,
        sample_limit: int,
        as_of_event_time_ms: int | None,
    ) -> list[dict[str, Any]]:
        return await self.db.rpc(
            "research_edge_scan_frozen",
            {
                "horizon_seconds": horizon_seconds,
                "fee_bps": fee_bps,
                "sample_limit": sample_limit,
                "as_of_event_time_ms": as_of_event_time_ms,
            },
        )

    async def wfo_scan(
        self,
        as_of_event_time_ms: int,
        horizon_seconds: int,
        sample_limit: int,
        purge_seconds: int,
        embargo_seconds: int,
        fee_bps: float,
        slippage_bps: float,
    ) -> list[dict[str, Any]]:
        return await self.db.rpc(
            "research_wfo_signal_scan",
            {
                "p_as_of_event_time_ms": as_of_event_time_ms,
                "p_horizon_seconds": horizon_seconds,
                "p_sample_limit": sample_limit,
                "p_purge_seconds": purge_seconds,
                "p_embargo_seconds": embargo_seconds,
                "p_fee_bps": fee_bps,
                "p_slippage_bps": slippage_bps,
            },
        )

    async def live_imbalance_signal(self, sample_limit: int) -> list[dict[str, Any]]:
        return await self.db.rpc("research_live_imbalance_signal", {"p_sample_limit": sample_limit})


def freshness(row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {"available": False, "stale": True, "age_ms": None}
    value = row.get("receive_time_ns")
    if value is not None:
        age_ms = max(0, time.time_ns() // 1_000_000 - int(value) // 1_000_000)
    else:
        timestamp = row.get("updated_at") or row.get("created_at")
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


app = FastAPI(title="BTCUSDT Research API", version="0.4.0", default_response_class=ORJSONResponse, lifespan=lifespan)


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


@app.get("/api/v1/research/edge-scan")
async def research_edge_scan(
    horizon_seconds: int = Query(60, ge=60, le=300),
    fee_bps: float | None = Query(None, ge=0, le=100),
    sample_limit: int = Query(50000, ge=5000, le=200000),
    as_of_event_time_ms: int | None = Query(None, ge=0),
) -> dict[str, Any]:
    if horizon_seconds not in (60, 120, 180, 300):
        raise HTTPException(status_code=400, detail="horizon_seconds must be one of 60, 120, 180, 300")
    try:
        rows = await app.state.live.edge_scan(horizon_seconds, fee_bps, sample_limit, as_of_event_time_ms)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="edge scan unavailable") from exc
    dataset_end = max((int(r["dataset_end_ms"]) for r in rows if r.get("dataset_end_ms") is not None), default=as_of_event_time_ms)
    dataset_start = min((int(r["dataset_start_ms"]) for r in rows if r.get("dataset_start_ms") is not None), default=None)
    return {"data": rows, "method": {"forward_return": "10000 * (future_mid - entry_mid) / entry_mid in bps", "buckets": 5, "future_match": "first valid same-session snapshot at/after horizon within 3 seconds", "net_ev_proxy": "gross forward return - observed spread_bps - configured round-trip fee_bps", "dataset_freeze": "entry observations are capped at as_of_event_time_ms minus horizon; repeated runs with the same cutoff use the same data window", "impact": "not included: stored feature snapshots do not contain full executable L2 levels", "status": "exploratory_screen_only"}, "parameters": {"horizon_seconds": horizon_seconds, "fee_bps": fee_bps, "sample_limit": sample_limit, "as_of_event_time_ms": as_of_event_time_ms}, "dataset": {"start_event_time_ms": dataset_start, "end_event_time_ms": dataset_end}}


@app.get("/api/v1/research/wfo")
async def research_wfo(
    horizon_seconds: int = Query(60, ge=60, le=300),
    sample_limit: int = Query(50000, ge=20000, le=200000),
    fee_bps: float = Query(4.0, ge=0, le=100),
    slippage_bps: float = Query(0.0, ge=0, le=100),
    purge_seconds: int = Query(60, ge=0, le=300),
    embargo_seconds: int = Query(60, ge=0, le=300),
) -> dict[str, Any]:
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


@app.get("/api/v1/signal/current")
async def current_signal(
    fee_bps: float = Query(4.0, ge=0, le=100),
    slippage_bps: float = Query(0.0, ge=0, le=100),
) -> dict[str, Any]:
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
