from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260912100000_hvol1_source_reconciliation.sql"
READINESS_MIGRATION = ROOT / "supabase/migrations/20260913111903_hvol1_readiness_temporal_gate_v2.sql"
FASTPATH_MIGRATION = ROOT / "supabase/migrations/20260914105000_hvol1_readiness_fastpath.sql"
PREREG = ROOT / "docs/H-VOL1_PREREGISTRATION.md"
API = ROOT / "src/btc_research/api.py"
DASHBOARD = ROOT / "dashboard/index.html"


def test_hvol1_migration_freezes_temporal_breakout_and_taker_flow_rules():
    sql = MIGRATION.read_text(encoding="utf-8")
    assert "research_hvol1_readiness" in sql
    assert "research_hvol1_scan_frozen" in sql
    assert "taker_buy_volume/o.volume" in sql
    assert "percentile_cont(.90)" in sql
    assert "percentile_cont(.10)" in sql
    assert "r.open_time_ms<p.oos_start_ms" in sql
    assert "rw.prior_count=120" in sql
    assert "rw.prior_first_ms=rw.trigger_ms-120*60*1000" in sql
    assert "rw.prior_last_ms=rw.trigger_ms-60*1000" in sql
    assert "rw.close>rw.prior_high" in sql
    assert "rw.close<rw.prior_low" in sql
    assert "c.trigger_ms+60000" in sql
    assert "e.open_time_ms+120*60*1000" in sql
    assert "f.entry_ms>=accepted.exit_ms" in sql
    assert "10::numeric" in sql and "12::numeric" in sql


def test_hvol1_readiness_requires_exact_real_minute_predecessor_and_continuity():
    sql = READINESS_MIGRATION.read_text(encoding="utf-8")
    assert "lag(o.open_time_ms,120)" in sql
    assert "lag(o.open_time_ms,1)" in sql
    assert "b.prior_first_ms=b.open_time_ms-120*60000" in sql
    assert "b.prior_last_ms=b.open_time_ms-60000" in sql
    assert "count(*) FILTER (WHERE prev_ms IS NOT NULL AND open_time_ms-prev_ms<>60000)" in sql
    assert "c.gap_count=0 AS continuity_ok" in sql
    assert "AND m.continuity_ok" in sql
    assert "READY_FOR_INDEPENDENT_AUDIT" in sql
    assert "false,'NOT GRANTED'" in sql


def test_hvol1_readiness_fastpath_is_truthful_and_timeout_safe():
    sql = FASTPATH_MIGRATION.read_text(encoding="utf-8")
    assert "IF p_oos_start_ms IS NULL THEN" in sql
    assert "p_oos_start_ms<p_as_of_ms" in sql
    assert "m.expected=m.candles" in sql
    assert "percentile_cont(.90)" in sql and "percentile_cont(.10)" in sql
    assert "outcome_run" in sql and "false,false,'NOT GRANTED'" in sql
    assert "research_hvol1_scan_frozen" not in sql


def test_hvol1_preregistration_blocks_outcome_until_boundary_and_audit():
    doc = PREREG.read_text(encoding="utf-8")
    assert "METHODOLOGY FROZEN / IMPLEMENTED / READINESS VISIBLE / OUTCOME UNRUN" in doc
    assert "NOT YET FROZEN" in doc
    assert "outcome status is **UNRUN**" in doc
    assert "authorization is **NOT GRANTED**" in doc
    assert "H-VOL1 outcome scan: **NOT RUN**" in doc
    assert "OOS outcome observed: **NO**" in doc


def test_hvol1_api_has_manual_scan_and_dashboard_readiness_only():
    api = API.read_text(encoding="utf-8")
    dashboard = DASHBOARD.read_text(encoding="utf-8")
    assert '"/api/v1/research/hvol1/readiness"' in api
    assert '"/api/v1/research/hvol1"' in api
    assert "research_hvol1_scan_frozen" in api
    assert '"trading_enabled":False' in api
    assert '"authorization":"NOT GRANTED"' in api
    assert "research_results?select=" in dashboard
    assert "research_lineage_manifest?select=" in dashboard
    assert "H-VOL1" in dashboard
    assert "research_hvol1_scan_public" not in dashboard
    assert "research_hvol1_scan_frozen" not in dashboard
    for token in ("H-VOL1", "readinessMetrics", "missing_minute_count", "oos_boundary_frozen"):
        assert token in dashboard
    assert "NOT GRANTED" in dashboard
    assert "Execution" in dashboard and "OFF" in dashboard


def test_hvol1_does_not_add_execution_path():
    api = API.read_text(encoding="utf-8")
    assert "order" not in api[api.index("async def research_hvol1_readiness"):api.index("async def research_hvol1(")]
    assert '"trading_enabled":False' in api
