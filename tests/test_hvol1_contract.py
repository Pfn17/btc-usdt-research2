from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260912100000_hvol1_source_reconciliation.sql"
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
    assert "safe('/api/v1/research/hvol1/readiness')" in dashboard
    assert "/api/v1/research/hvol1'" not in dashboard
    for token in ("H-VOL1", "hvol1Coverage", "hvol1Range", "hvol1P90", "hvol1P10", "hvol1Boundary", "hvol1Outcome", "hvol1Authorization"):
        assert token in dashboard
    assert 'hvol1Implementation">NOT VERIFIED' in dashboard
    assert 'hvol1Implementation\',\'READINESS COMPUTED' in dashboard
    assert 'hvol1Status\',\'READINESS UNAVAILABLE' in dashboard
    assert 'hvol1Status\',x.status||\'NOT_READY\'' in dashboard


def test_hvol1_does_not_add_execution_path():
    api = API.read_text(encoding="utf-8")
    assert "order" not in api[api.index("async def research_hvol1_readiness"):api.index("async def research_hvol1(")]
    assert '"trading_enabled":False' in api
