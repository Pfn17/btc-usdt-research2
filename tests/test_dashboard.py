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
    assert 'class="value observed"' in html


def test_dashboard_has_three_mode_archive_surface():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Inter,Arial,Helvetica,sans-serif" in html
    assert "#f0b90b" in html
    assert "#181a20" in html
    assert "Run comparison once" in html
    assert "reference specification" in html
    assert "independent specification" in html
    assert "value=\"terminal\"" in html
    assert "value=\"clean\"" in html
    assert "value=\"story\"" in html
    assert "id=\"chartPanel\"" in html
    assert "id=\"storyPanel\"" in html
    assert "id=\"marketChart\"" in html
    assert "story record" in html.lower()
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
