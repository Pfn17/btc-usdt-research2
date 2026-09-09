from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_asset_exists():
    dashboard = ROOT / "dashboard" / "index.html"
    assert dashboard.is_file()
    assert "HyperHan Lab" in dashboard.read_text(encoding="utf-8")


def test_dashboard_is_explicitly_read_only():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "read-only" in html
    assert "no value fabricated" in html
    assert "Execution" in html and "OFF" in html


def test_dashboard_is_an_owner_first_research_archive():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "research archive" in html.lower()
    assert "No validated edge." in html
    assert "LIVE EVIDENCE" in html
    assert "Find edges. Reject noise." not in html
    assert "gradient" not in html.lower()
    assert "Story" in html and "Terminal" in html and "Visual" in html
    assert 'id="page-story"' in html
    assert 'id="page-terminal"' in html
    assert 'id="page-visual"' in html
    assert "Research ledger" in html
    assert "H-FB1" in html and "H-SW1" in html


def test_dashboard_has_three_owner_surfaces_and_safe_refresh():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Reference specification" in html
    assert "Independent specification" in html
    assert 'data-page="story"' in html
    assert 'data-page="terminal"' in html
    assert 'data-page="visual"' in html
    assert 'id="marketChart"' in html
    assert "activePage==='terminal'?15000:300000" in html
    assert "toLocaleString('en-US'" in html
    assert "radial-gradient" not in html
    assert "linear-gradient" not in html
    assert "Inter,ui-sans-serif,system-ui" not in html


def test_landing_page_exists_and_links_to_console():
    landing = ROOT / "landing" / "index.html"
    assert landing.is_file()
    html = landing.read_text(encoding="utf-8")
    assert "HyperHan Lab" in html
    assert "dashboard" in html.lower()
