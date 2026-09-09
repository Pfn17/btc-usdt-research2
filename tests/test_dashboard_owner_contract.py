from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")


def test_research_rpcs_are_manual_and_not_on_operational_timer():
    assert "Read frozen comparison" in HTML
    assert "loadFrozen" in HTML
    assert "setInterval(loadPage,activePage==='terminal'?15000:300000)" in HTML
    assert "get('/api/v1/research/hfb1')" in HTML
    assert "get('/api/v1/research/sw1-claude')" in HTML
    assert "get('/api/v1/research/sw1-manus')" in HTML


def test_owner_visibility_and_no_fabrication_boundary():
    assert "no value fabricated" in HTML
    assert "Execution" in HTML and "OFF" in HTML
    assert "Result unavailable" in HTML
    assert "Research Archive" in HTML
    assert "UNAVAILABLE" in HTML
