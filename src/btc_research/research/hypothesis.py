from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class ExperimentFamily:
    family_id: str
    name: str
    protocol_version: str = "v1"

    def __post_init__(self) -> None:
        if not self.family_id or not self.name:
            raise ValueError("family_id and name are required")


@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    family_id: str
    statement: str
    horizon_seconds: int
    direction: str
    created_at: str

    def __post_init__(self) -> None:
        if self.direction not in {"long", "short", "two_sided"}:
            raise ValueError("direction must be long, short, or two_sided")
        if self.horizon_seconds <= 0:
            raise ValueError("horizon_seconds must be positive")

    @classmethod
    def create(cls, hypothesis_id: str, family_id: str, statement: str, horizon_seconds: int, direction: str) -> "Hypothesis":
        return cls(hypothesis_id, family_id, statement, horizon_seconds, direction, datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True, slots=True)
class ResearchFreeze:
    freeze_id: str
    family_id: str
    protocol_version: str
    parameters: dict[str, object]
    frozen_at: str
    fingerprint: str

    @classmethod
    def create(cls, freeze_id: str, family_id: str, parameters: dict[str, object], protocol_version: str = "v1") -> "ResearchFreeze":
        payload = json.dumps({"family_id": family_id, "protocol_version": protocol_version, "parameters": parameters}, sort_keys=True, separators=(",", ":"))
        fingerprint = sha256(payload.encode()).hexdigest()
        return cls(freeze_id, family_id, protocol_version, dict(parameters), datetime.now(timezone.utc).isoformat(), fingerprint)
