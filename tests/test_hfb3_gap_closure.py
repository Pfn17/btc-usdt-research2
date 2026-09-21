from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
ADDENDUM = (ROOT / "docs/H-FB3_AUDIT_ADDENDUM_2026-09-10.md").read_text(encoding="utf-8")
PREREG = (ROOT / "docs/H-FB3_PREREGISTRATION.md").read_text(encoding="utf-8")


def test_hfb3_persisted_result_is_read_from_public_api():
    assert "research_results?select=" in DASHBOARD
    assert "research_lineage_manifest?select=" in DASHBOARD
    assert "cost_adjusted_ev" in DASHBOARD
    assert "confidence_interval" in DASHBOARD
    assert "H-FB3" in DASHBOARD


def test_frozen_oos_window_is_explicit_and_reconciled():
    assert "OOS start: `2026-08-03T00:00:00Z`" in ADDENDUM
    assert "OOS complete-day end: `2026-09-09T23:59:59.999Z`" in ADDENDUM
    assert "Dataset SHA-256" in PREREG
    assert "OOS start: `2026-08-03T00:00:00Z`" in PREREG
    assert "OOS complete-day end: `2026-09-09T23:59:59.999Z`" in PREREG


def test_discarded_run_is_trace_only():
    assert "N=4,692" in ADDENDUM
    assert "discarded execution trace" in ADDENDUM
    assert "official result remains the later N=2,984 run" in ADDENDUM


def test_fdr_policy_is_prospective_not_retroactive():
    assert "Benjamini–Hochberg at `q = 0.05`" in ADDENDUM
    assert "No retroactive FDR correction" in ADDENDUM
    assert "No H-FB4 or later" in ADDENDUM
