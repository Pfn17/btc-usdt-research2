from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20260911090000_hmr1_extreme_mean_reversion.sql"
PREREG = ROOT / "docs/H-MR1_PREREGISTRATION.md"
API = ROOT / "src/btc_research/api.py"
DASHBOARD = ROOT / "dashboard/index.html"


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


def test_hmr1_dashboard_reads_persisted_result_without_running_outcome():
    dashboard = DASHBOARD.read_text(encoding="utf-8")
    assert "research_results?select=" in dashboard
    assert "research_lineage_manifest?select=" in dashboard
    assert "H-MR1" in dashboard
    assert "research_hmr1_scan_frozen" not in dashboard
    assert "READINESS ONLY · OUTCOME UNRUN" not in dashboard


def test_hmr1_does_not_add_execution_path():
    dashboard = DASHBOARD.read_text(encoding="utf-8")
    assert "research_hmr1_scan_frozen" not in dashboard
    assert "createOrder" not in dashboard and "place_order" not in dashboard
    assert "OFF" in dashboard
