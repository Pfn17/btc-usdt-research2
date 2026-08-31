"""Vercel read-only API entrypoint.

This module intentionally contains no trading/execution logic and never fabricates
market data. When Supabase has no fresh feature row, the API returns an explicit
unavailable/stale response instead of a placeholder.
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

app = FastAPI(title="BTCUSDT Research API", version="0.1.0")

STALE_AFTER_MS = int(os.getenv("FEATURE_STALE_AFTER_MS", "2000"))


def _supabase_config() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY") or ""
    if not url or not key:
        raise HTTPException(status_code=503, detail="supabase_not_configured")
    return url, key


async def _select(table: str, query: str) -> list[dict[str, Any]]:
    url, key = _supabase_config()
    endpoint = f"{url}/rest/v1/{table}?{query}"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(endpoint, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="supabase_unavailable") from exc
    if response.status_code >= 400:
        raise HTTPException(status_code=503, detail="supabase_query_failed")
    payload = response.json()
    return payload if isinstance(payload, list) else []


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "btc-usdt-research-api"}


@app.get("/api/v1/features/latest")
async def latest_features() -> dict[str, Any]:
    rows = await _select(
        "feature_snapshots",
        "select=*&order=created_at.desc&limit=1",
    )
    if not rows:
        raise HTTPException(status_code=503, detail="no_live_feature_data")

    row = rows[0]
    created_at = row.get("created_at")
    age_ms: float | None = None
    if created_at:
        # Supabase timestamps are ISO-8601; parse without adding a dependency.
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
            age_ms = max(0.0, (datetime.now(dt.tzinfo) - dt).total_seconds() * 1000.0)
        except ValueError:
            age_ms = None

    stale = age_ms is None or age_ms > STALE_AFTER_MS
    return {"status": "stale" if stale else "live", "age_ms": age_ms, "stale": stale, "data": row}


@app.get("/api/v1/collector/health")
async def collector_health() -> dict[str, Any]:
    rows = await _select(
        "collector_health",
        "select=*&order=created_at.desc&limit=1",
    )
    if not rows:
        raise HTTPException(status_code=503, detail="no_collector_health_data")
    return {"status": "ok", "data": rows[0]}


@app.get("/api/v1/session/current")
async def current_session() -> dict[str, Any]:
    rows = await _select(
        "research_sessions",
        "select=*&status=eq.running&order=started_at.desc&limit=1",
    )
    return {"status": "ok", "data": rows[0] if rows else None}


@app.websocket("/ws/features")
async def feature_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    last_id: str | None = None
    try:
        while True:
            rows = await _select(
                "feature_snapshots",
                "select=*&order=created_at.desc&limit=1",
            )
            if rows:
                row = rows[0]
                row_id = str(row.get("id") or row.get("created_at") or "")
                if row_id and row_id != last_id:
                    last_id = row_id
                    await websocket.send_json({"type": "feature", "data": row})
            else:
                await websocket.send_json({"type": "status", "status": "no_data"})
            await __import__("asyncio").sleep(0.5)
    except WebSocketDisconnect:
        return
    except Exception:
        try:
            await websocket.send_json({"type": "status", "status": "degraded"})
        except Exception:
            pass
