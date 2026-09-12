from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260911090000_hmr1_extreme_mean_reversion.sql"
PREREG = ROOT / "docs/H-MR1_PREREGISTRATION.md"
API = ROOT / "src/btc_research/api.py"


def test_hmr1_has_separate_preregistration_and_frozen_rpc():
    sql = MIGRATION.read_text(encoding="utf-8")
    doc = PREREG.read_text(encoding="utf-8")
    assert "research_hmr1_scan_frozen" in sql
    assert "percentile_cont(0.95)" in sql
    assert "r.open_time_ms<p.oos_start_ms" in sql
    assert "r.open_time_ms>=p.oos_start_ms" in sql
    assert "p.stress_rt_bps" in sql
    assert "nonoverlap" in sql
    assert "H-MR1" in doc
    assert "No outcome scan has been run" in doc
    assert "INCONCLUSIVE" in doc


def test_hmr1_api_is_manual_and_read_only():
    api = API.read_text(encoding="utf-8")
    assert '"/api/v1/research/hmr1"' in api
    assert "research_hmr1_scan_frozen" in api
    assert '"trading_enabled":False' in api
    assert '"research_status":"frozen_scan_unverified"' in api
    assert "setInterval" not in api[api.index('async def research_hmr1'):]


def test_hmr1_does_not_modify_frontend():
    dashboard = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    landing = (ROOT / "landing/index.html").read_text(encoding="utf-8")
    assert "safe('/api/v1/research/hmr1/readiness')" in dashboard
    assert "safe('/api/v1/research/hmr1')" not in dashboard
    assert "/api/v1/research/hmr1" not in landing
