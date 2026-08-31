from __future__ import annotations

import asyncio
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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
    # The API must never receive the collector's service-role credential.
    key = os.environ.get("SUPABASE_ANON_KEY", "") or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_PUBLISHABLE_KEY) are required")
    return APIConfig(url=url, key=key, symbol=os.environ.get("BTC_SYMBOL", "BTCUSDT").upper())


class SupabaseReadClient:
    def __init__(self, config: APIConfig) -> None:
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=f"{config.url}/rest/v1",
            timeout=httpx.Timeout(5.0, connect=2.0),
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
        rows = await self.db.select(
            "collector_health",
            "select=*&order=updated_at.desc&limit=1",
        )
        return rows[0] if rows else None

    async def current_session(self) -> dict[str, Any] | None:
        rows = await self.db.select(
            "research_sessions",
            "select=id,symbol,mode,status,started_at,last_heartbeat_at,stopped_at&status=eq.running&order=last_heartbeat_at.desc&limit=1",
        )
        return rows[0] if rows else None


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


app = FastAPI(
    title="BTCUSDT Research API",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


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
        return {
            "status": "ok" if session and feature_fresh["available"] and not feature_fresh["stale"] else "degraded",
            "symbol": app.state.config.symbol,
            "collector_session": session,
            "feature_freshness": feature_fresh,
        }
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
