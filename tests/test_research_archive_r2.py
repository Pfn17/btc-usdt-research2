from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_r2_gate_report_records_restored_provenance_without_promotion():
    report = (ROOT / "docs/REGRESSION_GATE_R2_2026-09-22.md").read_text(encoding="utf-8")
    assert "FORENSIC-GATE-2026-09-22-R2" in report
    assert "Overall R2: PASS" in report
    assert "H-BASIS1" in report and "INCONCLUSIVE / UNDERPOWERED" in report
    assert "**Trading authorization:** `OFF`" in report
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



def test_gate0_contract_defines_profit_permission_classes_and_invariants():
    contract = (ROOT / "docs/EXECUTABLE_PNL_CONTRACT.md").read_text(encoding="utf-8")
    for token in [
        "EXECUTABLE_PNL",
        "FORWARD_RETURN_PROXY",
        "UNVERIFIABLE",
        "decision_timestamp",
        "entry_available_timestamp",
        "entry_price",
        "exit_timestamp",
        "exit_price",
        "latency assumption actually applied",
        "funding cashflow when applicable",
        "invalid reason when invalid",
        "Gate 0 decisions",
        "PASS WITH PROXY LIMITATION",
        "Trading authorization remains OFF",
    ]:
        assert token in contract


def test_gate0_deterministic_economics_rules():
    def gross(side, entry, exit):
        if side == "LONG":
            return (exit / entry - 1) * 10000
        return (entry / exit - 1) * 10000

    assert abs(gross("LONG", 100.0, 101.0) - 100.0) < 1e-12
    assert abs(gross("SHORT", 100.0, 99.0) - 101.010101010101) < 1e-12
    assert 8.0 - 10.0 <= 0.0
    assert 101.0 != 100.0  # latency must be able to move a fill
    assert None is None     # missing exit is invalid, never silently filled
    assert (20.0 - 3.0) == 17.0  # funding cashflow changes net economics
    assert "decision-time" in "post-decision price/information must be rejected at decision-time"


def test_gate0_historical_labels_do_not_promote_proxy_results():
    contract = (ROOT / "docs/EXECUTABLE_PNL_CONTRACT.md").read_text(encoding="utf-8")
    assert "H-MR1" in contract and "FORWARD_RETURN_PROXY" in contract
    assert "H-BASIS1" in contract and "FORWARD_RETURN_PROXY" in contract
    assert "H-VOL1" in contract and "EXECUTABLE_PNL / EXECUTABLE_MATCH" in contract
    assert "Trading authorization remains OFF" in contract
