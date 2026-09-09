from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_asset_exists():
    dashboard = ROOT / "dashboard" / "index.html"
    assert dashboard.is_file()
    assert "HyperHan Lab" in dashboard.read_text(encoding="utf-8")


def test_dashboard_is_explicitly_read_only():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "read-only" in html
    assert "fabricate" in html


def test_dashboard_is_a_research_archive():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "research archive" in html.lower()
    assert "No validated edge." in html
    assert "LIVE EVIDENCE" in html
    assert "Find edges. Reject noise." not in html
    assert 'id="systemMap"' not in html
    assert 'id="lifecycle"' not in html
    assert 'id="start"' not in html
    assert 'id="run"' not in html
    assert "Observed funding" in html
    assert 'id="page-overview"' in html


def test_dashboard_has_three_mode_archive_surface():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Inter,ui-sans-serif,system-ui" in html
    assert "--accent:#00d4ff" in html
    assert "--yellow:#f0b90b" in html
    assert "Run comparison once" in html
    assert "reference specification" in html
    assert "independent specification" in html
    assert "data-page=\"overview\"" in html
    assert "data-page=\"visual\"" in html
    assert "data-page=\"story\"" in html
    assert "id=\"page-overview\"" in html
    assert "id=\"page-visual\"" in html
    assert "id=\"page-story\"" in html
    assert "id=\"marketChart\"" in html
    assert "activePage==='overview'?15000:300000" in html
    assert "if(activePage==='overview')base.push" in html
    assert "Apple" not in html
    assert "archive-tab" not in html
    assert "evidencePulse" not in html
    assert "telemetry" not in html
    assert "data-panel" not in html


def test_landing_page_exists_and_links_to_console():
    landing = ROOT / "landing" / "index.html"
    assert landing.is_file()
    html = landing.read_text(encoding="utf-8")
    assert "HyperHan Lab" in html
    assert "Find edges." in html
    assert 'href="/"' in html
    assert "no substitute data" in html
