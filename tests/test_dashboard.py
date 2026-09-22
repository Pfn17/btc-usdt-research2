from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_asset_exists():
    dashboard = ROOT / "dashboard" / "index.html"
    assert dashboard.is_file()
    assert "HyperHan Lab" in dashboard.read_text(encoding="utf-8")


def test_dashboard_is_explicitly_read_only():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "RESEARCH ONLY" in html
    assert "trading disabled" in html
    assert "Execution" in html and "OFF" in html


def test_dashboard_is_an_owner_first_research_archive():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "research record" in html.lower()
    assert "What is happening now" in html
    assert "What the database can actually support" in html
    assert "Find edges. Reject noise." not in html
    assert "Research control room" in html
    assert "Execution" in html and "OFF" in html
    assert "gradient" not in html.lower()


def test_dashboard_has_research_surfaces_and_safe_refresh():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert 'id="binancePrice"' in html
    assert 'id="roomHypotheses"' in html
    assert "research_hypotheses?select=" in html
    assert "const schedule={research:60000,market:15000}" in html
    assert "no value fabricated" in html
    assert "governance/summary" not in html
    assert "toLocaleString('en-US'" in html
    assert "radial-gradient" not in html
    assert "linear-gradient" not in html


def test_dashboard_provider_states_are_evidence_aware():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "READY · OBSERVED" in html
    assert "RAILWAY" in html and "UNVERIFIED" in html
    assert "BUILDING*" not in html
    assert "FAILED*" not in html
    assert "e5110aa" not in html


def test_landing_page_exists_and_links_to_console():
    landing = ROOT / "landing" / "index.html"
    assert landing.is_file()
    html = landing.read_text(encoding="utf-8")
    assert "HyperHan Lab" in html
    assert "dashboard" in html.lower()


def test_dashboard_interactions_have_real_handlers_and_no_broken_market_renderer():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "function openSearch()" in html
    assert 'data-target="sources"' in html
    assert 'data-doc="docs/EXECUTABLE_PNL_CONTRACT.md"' in html
    assert "return allOk;" in html
    assert "return true;" in html
    assert "document.getElementById('binancePrice').textContent='$'+Number(x.lastPrice)" in html
    assert "textContent='document.getElementById('binanceMeta')" not in html


def test_dashboard_live_refresh_has_backoff_and_does_not_poll_when_hidden():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "const schedule={research:60000,market:15000}" in html
    assert "Math.pow(2,researchBackoff)" in html
    assert "Math.pow(2,marketBackoff)" in html
    assert "document.addEventListener('visibilitychange'" in html


def test_dashboard_exposes_canonical_archive_metadata_without_raw_imports():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    migration = (ROOT / "supabase/migrations/20260922203000_public_read_research_archive_views.sql").read_text(encoding="utf-8")
    assert 'id="datasetRegistry"' in html
    assert 'id="canonicalHypotheses"' in html
    assert "research_dataset_registry?select=" in html
    assert "research_hypothesis_records?select=" in html
    assert "research_agent_activity_public?select=" in html
    assert "NO EXTERNAL DATASETS REGISTERED" in html
    assert "revoke insert, update, delete" in migration.lower()
    assert "grant select" in migration.lower()
