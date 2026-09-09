from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sw1_migration_freezes_core_parameters() -> None:
    sql = (ROOT / "supabase/migrations/20260908_hsw1_swing_lite.sql").read_text(encoding="utf-8")
    assert "research_sw1_manus_scan_frozen" in sql
    assert "research_sw1_scan_frozen" not in sql
    assert "24::bigint * 60 * 60 * 1000" in sql
    assert "LIMIT 3" in sql
    assert "2*(p.fee_bps+p.slippage_bps)" in sql
    assert "quarter_" in sql


def test_sw1_api_is_read_only_and_parameter_locked() -> None:
    api = (ROOT / "src/btc_research/api.py").read_text(encoding="utf-8")
    assert '@app.get("/api/v1/research/sw1-manus")' in api
    assert '@app.get("/api/v1/research/sw1-claude")' in api
    assert 'research_sw1_manus_scan_frozen' in api
    assert 'research_sw1_scan_frozen' in api
    assert '"trading_enabled":False' in api
    assert 'sw1_scan(as_of_ms,4.0,1.0,3)' in api


def test_dashboard_has_real_sw1_bindings_and_no_execution_claim() -> None:
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "/api/v1/research/sw1-manus" in html
    assert "/api/v1/research/sw1-claude" in html
    assert 'id="sw1RefN"' in html
    assert 'id="sw1IndN"' in html
    assert "Reference specification" in html
    assert "Independent specification" in html
    assert "No value fabricated" in html
    assert "Execution" in html and "OFF" in html
