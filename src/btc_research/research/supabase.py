from __future__ import annotations

import os
from dataclasses import asdict, is_dataclass
from typing import Any

import httpx


class SupabaseResearchClient:
    """Small PostgREST client for the M5 research registry.

    Required environment variables:
      SUPABASE_URL
      SUPABASE_SERVICE_ROLE_KEY (server-side only; never expose to frontend)
    """

    def __init__(self, url: str | None = None, service_role_key: str | None = None, timeout: float = 10.0) -> None:
        self.url = (url or os.environ.get("SUPABASE_URL", "")).rstrip("/")
        self.key = service_role_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        self._client = httpx.Client(
            base_url=f"{self.url}/rest/v1",
            timeout=timeout,
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
        )

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

    def insert(self, table: str, rows: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        response = self._client.post(f"/{table}", json=rows, headers={"Prefer": "return=representation"})
        response.raise_for_status()
        return response.json()

    def select(self, table: str, query: str = "select=*&limit=100") -> list[dict[str, Any]]:
        response = self._client.get(f"/{table}?{query}")
        response.raise_for_status()
        return response.json()

    def insert_hypothesis(self, hypothesis: Any, target_definition: dict[str, Any] | None = None, feature_set: list[str] | None = None) -> list[dict[str, Any]]:
        return self.insert("research_hypotheses", {
            "id": hypothesis.hypothesis_id,
            "family_id": hypothesis.family_id,
            "hypothesis_key": hypothesis.hypothesis_id,
            "statement": hypothesis.statement,
            "direction": hypothesis.direction,
            "horizon_seconds": hypothesis.horizon_seconds,
            "target_definition": target_definition or {},
            "feature_set": feature_set or [],
            "created_at": hypothesis.created_at,
        })

    def insert_family(self, family: Any) -> list[dict[str, Any]]:
        return self.insert("experiment_families", {
            "id": family.family_id,
            "family_key": family.family_id,
            "protocol_version": family.protocol_version,
            "description": family.name,
        })

    def insert_batch(self, family_id: str, batch_key: str, config_hash: str, hypothesis_hash: str, code_version: str, dataset_hash: str | None = None) -> list[dict[str, Any]]:
        return self.insert("experiment_batches", {
            "family_id": family_id,
            "batch_key": batch_key,
            "config_hash": config_hash,
            "hypothesis_hash": hypothesis_hash,
            "code_version": code_version,
            "dataset_hash": dataset_hash,
        })

    def insert_model_run(self, batch_id: str, model_name: str, feature_schema_hash: str, parameters: dict[str, Any], train_samples: int | None = None, test_samples: int | None = None) -> list[dict[str, Any]]:
        return self.insert("model_runs", {
            "batch_id": batch_id,
            "model_name": model_name,
            "feature_schema_hash": feature_schema_hash,
            "parameters": parameters,
            "train_samples": train_samples,
            "test_samples": test_samples,
        })

    def insert_result(self, model_run_id: str, result: dict[str, Any]) -> list[dict[str, Any]]:
        return self.insert("research_results", {"model_run_id": model_run_id, **result})
