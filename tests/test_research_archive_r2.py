from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_r2_gate_report_records_restored_provenance_without_promotion():
    report = (ROOT / "docs/REGRESSION_GATE_R2_2026-09-22.md").read_text(encoding="utf-8")
    assert "FORENSIC-GATE-2026-09-22-R2" in report
    assert "Overall R2: PASS" in report
    assert "H-BASIS1" in report and "INCONCLUSIVE / UNDERPOWERED" in report
    assert "Trading authorization: `OFF`" in report
    assert "does not reopen hypothesis generation" in report


def test_dashboard_publishes_all_historical_results_and_role_status():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    for token in [
        "Founder &amp; Principal Researcher",
        "PAUSED — NO NEW HYPOTHESES",
        "Current Gate R2",
        "APPEND-ONLY",
        "Trading authorization",
        "H-FB3",
        "4H Momentum",
        "Funding-sign",
        "Funding + 24h return",
        "H-MR1",
        "H-VOL1",
        "H-SW1",
        "H-BASIS1",
        "H-BASIS1 detail",
        "PROVENANCE RESTORED · REPLAY MATCH",
    ]:
        assert token in html


def test_dashboard_keeps_execution_off_and_no_order_path():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "Execution" in html and "OFF" in html
    assert "No live signals or promoted strategies" in html
    assert "order" not in html.lower() or "order path" in html.lower()


def test_dashboard_archive_does_not_execute_live_outcome_scans():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "No live outcome scan is executed from the dashboard." in html
    assert "research_funding_hfb1" not in html
    assert "research_sw1_scan_frozen" not in html
    assert "research_ohlcv_momentum_frozen" not in html
    assert "research_hvol1_scan_frozen" not in html
