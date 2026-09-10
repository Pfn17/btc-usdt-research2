from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_asset_exists():
    dashboard = ROOT / "dashboard" / "index.html"
    assert dashboard.is_file()
    assert "HyperHan Lab" in dashboard.read_text(encoding="utf-8")


def test_dashboard_is_explicitly_read_only():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "READ-ONLY" in html
    assert "Never inferred" in html
    assert "Execution" in html and "OFF" in html


def test_dashboard_is_an_owner_first_research_archive():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "research archive" in html.lower()
    assert "No validated edge." in html
    assert "Current position" in html
    assert "Find edges. Reject noise." not in html
    assert "gradient" not in html.lower()
    assert "Evidence you can inspect" in html
    assert "System state and provenance" in html
    assert "Funding follow-sign" in html and "Swing" in html


def test_dashboard_has_three_owner_surfaces_and_safe_refresh():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Reference study" in html
    assert "Independent study" in html
    assert 'id="marketChart"' in html
    assert "setInterval(loadOperational,15000)" in html
    assert "setInterval(loadResearch,900000)" in html
    assert "Loading current research data" in html
    assert "zero decision boundary" in html
    assert "governance/summary" in html
    assert "toLocaleString('en-US'" in html
    assert "radial-gradient" not in html
    assert "linear-gradient" not in html
    assert "Inter,ui-sans-serif,system-ui" in html


def test_landing_page_exists_and_links_to_console():
    landing = ROOT / "landing" / "index.html"
    assert landing.is_file()
    html = landing.read_text(encoding="utf-8")
    assert "HyperHan Lab" in html
    assert "dashboard" in html.lower()
