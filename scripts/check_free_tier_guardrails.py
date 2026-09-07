#!/usr/bin/env python3
"""Fail closed on obvious free-tier and provenance regressions.

This check is intentionally deterministic and has no network calls. It does not
measure provider quotas; provider usage must be checked from the provider UI/API
before bounded backfills or deployments.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "AGENTS.md",
    ROOT / "docs" / "FREE_TIER_GOVERNANCE.md",
    ROOT / "docs" / "BACKUP_POLICY.md",
    ROOT / "research-vault" / "policies" / "dashboard-live-only.md",
]
for path in required:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"missing required governance file: {path}")

secret_patterns = [
    re.compile(r"(?i)(service[_-]?role|api[_-]?(key|secret)|jwt[_-]?secret)\s*[:=]\s*[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"(?i)\b(sk|pk)_[A-Za-z0-9]{20,}\b"),
]
allowed_suffixes = {".md", ".json", ".ts", ".svg", ".html", ".py", ".sql", ".yml", ".yaml", ".txt"}
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.suffix not in allowed_suffixes:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in secret_patterns:
        if pattern.search(text) and "example" not in path.name.lower() and "governance" not in str(path).lower():
            raise SystemExit(f"possible secret-like assignment in {path}")

# Refetchable market dumps must not be added under the durable vault.
for path in (ROOT / "research-vault").rglob("*"):
    if path.is_file() and path.suffix.lower() in {".csv", ".parquet", ".feather", ".db"}:
        raise SystemExit(f"raw data file is not allowed in research-vault: {path}")

print("free-tier guardrails: OK")
