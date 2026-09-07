from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_asset_exists():
    dashboard = ROOT / "dashboard" / "index.html"
    assert dashboard.is_file()
    assert "HyperHan Research Archive" in dashboard.read_text(encoding="utf-8")


def test_dashboard_is_explicitly_read_only():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "read-only" in html
    assert "fabricate" in html


def test_dashboard_is_a_research_archive():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Research Archive" in html
    assert "No validated edge." in html
    assert "LIVE EVIDENCE" in html
    assert "Find edges. Reject noise." not in html
    assert 'id="systemMap"' not in html
    assert 'id="lifecycle"' not in html
    assert 'id="start"' not in html
    assert 'id="run"' not in html
    assert "Observed funding direction" in html
    assert "class=\"value observed\"" in html


def test_dashboard_has_instrument_style_local_interactions():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "SF Pro Display" in html
    assert "data:image/svg+xml" in html
    assert "archive-tab" in html
    assert "setupTabs" in html
    assert "updateClock" in html
    assert "EXECUTION OFF" in html
    assert "No new endpoint, storage, or trading signal" in html
    assert "fetch('/api/v1/market/ohlcv/latest?limit=3')" not in html


def test_landing_page_exists_and_links_to_console():
    landing = ROOT / "landing" / "index.html"
    assert landing.is_file()
    html = landing.read_text(encoding="utf-8")
    assert "HyperHan Lab" in html
    assert "Find edges." in html
    assert 'href="/"' in html
    assert "no substitute data" in html
