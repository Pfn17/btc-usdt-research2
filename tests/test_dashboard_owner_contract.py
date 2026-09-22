from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")


def test_dashboard_refreshes_at_bounded_cadence():
    assert "async function refresh()" in HTML
    assert "const schedule={research:60000,market:15000}" in HTML
    assert "cache:'no-store'" in HTML
    assert "research_hypotheses?select=" in HTML


def test_owner_visibility_and_no_fabrication_boundary():
    assert "no value fabricated" in HTML
    assert "Execution" in HTML and "OFF" in HTML
    assert "UNAVAILABLE" in HTML
    assert "NOT GRANTED" in HTML
    assert "RESEARCH ARCHIVE" in HTML
    assert "governance/summary" not in HTML
    assert "Project memory" not in HTML
    assert "owner_decisions?select=" in HTML
    assert "contamination_intervals?select=" in HTML


def test_direct_supabase_read_is_public_read_only_surface():
    assert "https://xaqsntunrqvqpzlbeutt.supabase.co" in HTML
    assert "rest/v1/" in HTML
    assert "order" in HTML
    assert "Authorization:'Bearer '+KEY" in HTML


def test_hypothesis_registry_policy_is_select_only():
    migration = (ROOT / "supabase/migrations/20260919221500_research_hypotheses_public_read.sql").read_text(encoding="utf-8")
    assert "research_hypotheses_read_public" in migration
    assert "FOR SELECT" in migration
    assert "GRANT SELECT" in migration
    assert "REVOKE INSERT, UPDATE, DELETE" in migration
