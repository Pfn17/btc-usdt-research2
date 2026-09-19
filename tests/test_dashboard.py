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
    assert "What exists today" in html
    assert "Frozen boundary & data integrity" in html
    assert "Find edges. Reject noise." not in html
    assert "Research control room" in html
    assert "Execution" in html and "OFF" in html
    assert "gradient" not in html.lower()


def test_dashboard_has_research_surfaces_and_safe_refresh():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert 'id="binancePrice"' in html
    assert 'id="roomHypotheses"' in html
    assert "research_hypotheses?select=" in html
    assert "setInterval(refresh,60000)" in html
    assert "no value fabricated" in html
    assert "governance/summary" not in html
    assert "toLocaleString('en-US'" in html
    assert "radial-gradient" not in html
    assert "linear-gradient" not in html


def test_dashboard_provider_states_are_evidence_aware():
    html = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")
    assert "READY · OBSERVED" in html
    assert "d16c601" in html
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
