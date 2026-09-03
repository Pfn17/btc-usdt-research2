from __future__ import annotations

import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

import httpx


class SupabaseResearchClient:
    """Small PostgREST client for the research registry."""

    _TABLE_CONTRACTS: dict[str, tuple[frozenset[str], frozenset[str]]] = {
        "feature_snapshots": (
            frozenset({"session_id", "symbol", "event_time_ms", "receive_time_ns", "book_update_id", "mid_price", "spread", "spread_bps", "microprice", "imbalance_1", "imbalance_n", "bid_depth_n", "ask_depth_n", "order_flow_1s", "volatility_1s", "book_pressure", "compute_time_ns"}),
            frozenset({"session_id", "symbol", "event_time_ms", "receive_time_ns", "book_update_id", "mid_price", "spread", "spread_bps", "microprice", "imbalance_1", "imbalance_n", "bid_depth_n", "ask_depth_n", "order_flow_1s", "volatility_1s", "book_pressure"}),
        ),
        "paper_signals": (
            frozenset({"session_id", "event_time_ms", "direction", "confidence", "expected_move", "horizon_seconds", "data_quality", "risk_status", "rationale"}),
            frozenset({"session_id", "event_time_ms", "direction", "data_quality", "risk_status"}),
        ),
        "contamination_intervals": (
            frozenset({"session_id", "started_at", "ended_at", "reason"}),
            frozenset({"session_id", "started_at", "reason"}),
        ),
        "collector_health": (
            frozenset({"session_id", "feed_status", "integrity_status", "events_received", "events_applied", "duplicate_events", "sequence_gaps", "resync_count", "stale_after_ms", "latency_ms", "contamination_active", "updated_at", "last_update_id"}),
            frozenset({"session_id", "feed_status", "integrity_status", "events_received", "events_applied", "duplicate_events", "sequence_gaps", "resync_count", "contamination_active", "updated_at"}),
        ),
        "ohlcv_1m": (
            frozenset({"symbol", "interval", "open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume", "quote_volume", "trade_count", "taker_buy_volume", "taker_buy_quote_volume", "collected_at"}),
            frozenset({"symbol", "interval", "open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume", "quote_volume", "trade_count", "taker_buy_volume", "taker_buy_quote_volume"}),
        ),
        "funding_basis_snapshots": (
            frozenset({"symbol", "server_time_ms", "mark_price", "index_price", "last_funding_rate", "next_funding_time_ms", "collected_at"}),
            frozenset({"symbol", "server_time_ms", "mark_price", "index_price", "last_funding_rate"}),
        ),
        "funding_rate_events": (
            frozenset({"symbol", "funding_time_ms", "funding_rate", "mark_price", "collected_at"}),
            frozenset({"symbol", "funding_time_ms", "funding_rate"}),
        ),
    }

    def __init__(self, url: str | None = None, service_role_key: str | None = None, timeout: float = 10.0) -> None:
        self.url = (url or os.environ.get("SUPABASE_URL", "")).rstrip("/")
        self.key = service_role_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        self._client = httpx.Client(base_url=f"{self.url}/rest/v1", timeout=timeout, headers={"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SupabaseResearchClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def _payload(value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        return value

    @classmethod
    def _validate_payload(cls, table: str, payload: dict[str, Any]) -> None:
        contract = cls._TABLE_CONTRACTS.get(table)
        if contract is None:
            return
        allowed, required = contract
        unknown = set(payload) - allowed
        missing = required - set(payload)
        if unknown:
            raise ValueError(f"{table} payload has unknown columns: {sorted(unknown)}")
        if missing:
            raise ValueError(f"{table} payload is missing required columns: {sorted(missing)}")

    @classmethod
    def _validate_rows(cls, table: str, rows: dict[str, Any] | list[dict[str, Any]]) -> None:
        payloads = rows if isinstance(rows, list) else [rows]
        for payload in payloads:
            if not isinstance(payload, dict):
                raise TypeError(f"{table} payload must be a dict")
            cls._validate_payload(table, payload)

    def insert(self, table: str, rows: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        self._validate_rows(table, rows)
        response = self._client.post(f"/{table}", json=rows, headers={"Prefer": "return=representation"})
        response.raise_for_status()
        return response.json()

    def upsert(self, table: str, rows: dict[str, Any] | list[dict[str, Any]], on_conflict: str) -> list[dict[str, Any]]:
        self._validate_rows(table, rows)
        response = self._client.post(f"/{table}?on_conflict={quote(on_conflict, safe=',')}", json=rows, headers={"Prefer": "resolution=merge-duplicates,return=representation"})
        response.raise_for_status()
        return response.json()

    def select(self, table: str, query: str = "select=*&limit=100") -> list[dict[str, Any]]:
        response = self._client.get(f"/{table}?{query}")
        response.raise_for_status()
        return response.json()

    def update(self, table: str, filters: str, values: dict[str, Any]) -> list[dict[str, Any]]:
        response = self._client.patch(f"/{table}?{filters}", json=values, headers={"Prefer": "return=representation"})
        response.raise_for_status()
        return response.json()

    def upsert_ohlcv_1m(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []
        return self.upsert("ohlcv_1m", rows, "symbol,interval,open_time_ms")

    def upsert_funding_basis(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []
        return self.upsert("funding_basis_snapshots", rows, "symbol,server_time_ms")

    def upsert_funding_events(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []
        return self.upsert("funding_rate_events", rows, "symbol,funding_time_ms")

    def stop_stale_sessions(self, owner_id: str = "railway-worker", stale_after_seconds: int = 120) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=stale_after_seconds)).isoformat()
        queries = (
            f"select=id&owner_id=eq.{quote(owner_id)}&status=eq.running&last_heartbeat_at=lt.{quote(cutoff)}&limit=100",
            f"select=id&owner_id=eq.{quote(owner_id)}&status=eq.running&last_heartbeat_at=is.null&started_at=lt.{quote(cutoff)}&limit=100",
        )
        ids: set[str] = set()
        for query in queries:
            ids.update(str(row["id"]) for row in self.select("research_sessions", query))
        for session_id in ids:
            self.stop_session(session_id)
        return len(ids)

    def insert_session(self, symbol: str, mode: str = "paper", owner_id: str = "railway-worker") -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        return self.insert("research_sessions", {"owner_id": owner_id, "symbol": symbol.upper(), "mode": mode, "status": "running", "started_at": now, "last_heartbeat_at": now})

    def heartbeat_session(self, session_id: str) -> list[dict[str, Any]]:
        return self.update("research_sessions", f"id=eq.{session_id}", {"last_heartbeat_at": datetime.now(timezone.utc).isoformat()})

    def stop_session(self, session_id: str) -> list[dict[str, Any]]:
        return self.update("research_sessions", f"id=eq.{session_id}", {"status": "stopped", "stopped_at": datetime.now(timezone.utc).isoformat()})

    def insert_feature_snapshot(self, session_id: str, snapshot: Any) -> list[dict[str, Any]]:
        payload = self._payload(snapshot)
        if not isinstance(payload, dict):
            raise TypeError("feature snapshot must be a dataclass or dict")
        return self.insert("feature_snapshots", {"session_id": session_id, **payload})

    def insert_feature_snapshots(self, session_id: str, snapshots: list[Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for snapshot in snapshots:
            payload = self._payload(snapshot)
            if not isinstance(payload, dict):
                raise TypeError("feature snapshot must be a dataclass or dict")
            rows.append({"session_id": session_id, **payload})
        if not rows:
            return []
        return self.insert("feature_snapshots", rows)

    def insert_paper_signal(self, session_id: str, signal: Any) -> list[dict[str, Any]]:
        payload = self._payload(signal)
        if not isinstance(payload, dict):
            raise TypeError("paper signal must be a dataclass or dict")
        return self.insert("paper_signals", {"session_id": session_id, **payload})

    def insert_collector_health(self, session_id: str, health: dict[str, Any]) -> list[dict[str, Any]]:
        return self.upsert("collector_health", {"session_id": session_id, **health}, "session_id")

    def insert_contamination_interval(self, session_id: str, interval: Any) -> list[dict[str, Any]]:
        payload = self._payload(interval)
        if not isinstance(payload, dict):
            raise TypeError("contamination interval must be a dataclass or dict")
        if "start_ms" in payload:
            payload["started_at"] = datetime.fromtimestamp(payload.pop("start_ms") / 1000, tz=timezone.utc).isoformat()
        if "end_ms" in payload:
            end_ms = payload.pop("end_ms")
            payload["ended_at"] = None if end_ms is None else datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc).isoformat()
        return self.insert("contamination_intervals", {"session_id": session_id, **payload})

    def insert_hypothesis(self, hypothesis: Any, target_definition: dict[str, Any] | None = None, feature_set: list[str] | None = None) -> list[dict[str, Any]]:
        return self.insert("research_hypotheses", {"id": hypothesis.hypothesis_id, "family_id": hypothesis.family_id, "hypothesis_key": hypothesis.hypothesis_id, "statement": hypothesis.statement, "direction": hypothesis.direction, "horizon_seconds": hypothesis.horizon_seconds, "target_definition": target_definition or {}, "feature_set": feature_set or [], "created_at": hypothesis.created_at})

    def insert_family(self, family: Any) -> list[dict[str, Any]]:
        return self.insert("experiment_families", {"id": family.family_id, "family_key": family.family_id, "protocol_version": family.protocol_version, "description": family.name})

    def insert_batch(self, family_id: str, batch_key: str, config_hash: str, hypothesis_hash: str, code_version: str, dataset_hash: str | None = None) -> list[dict[str, Any]]:
        return self.insert("experiment_batches", {"family_id": family_id, "batch_key": batch_key, "config_hash": config_hash, "hypothesis_hash": hypothesis_hash, "code_version": code_version, "dataset_hash": dataset_hash})

    def insert_model_run(self, batch_id: str, model_name: str, feature_schema_hash: str, parameters: dict[str, Any], train_samples: int | None = None, test_samples: int | None = None) -> list[dict[str, Any]]:
        return self.insert("model_runs", {"batch_id": batch_id, "model_name": model_name, "feature_schema_hash": feature_schema_hash, "parameters": parameters, "train_samples": train_samples, "test_samples": test_samples})

    def insert_result(self, model_run_id: str, result: dict[str, Any]) -> list[dict[str, Any]]:
        return self.insert("research_results", {"model_run_id": model_run_id, **result})