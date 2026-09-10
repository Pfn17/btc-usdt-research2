from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")


def test_research_rpcs_are_manual_and_not_on_operational_timer():
    assert "Read frozen comparison" in HTML
    assert "loadFrozen" in HTML
    assert "setInterval(loadTerminal,15000)" in HTML
    assert "setInterval(()=>{loadStory();loadVisual();loadFrozen()},900000)" in HTML
    assert "get('/api/v1/research/hfb1')" in HTML
    assert "get('/api/v1/research/sw1-claude')" in HTML
    assert "get('/api/v1/research/sw1-manus')" in HTML


def test_owner_visibility_and_no_fabrication_boundary():
    assert "no value fabricated" in HTML
    assert "Execution" in HTML and "OFF" in HTML
    assert "Result unavailable" in HTML
    assert "Research Archive" in HTML
    assert "UNAVAILABLE" in HTML
    assert "STALE" in HTML
    assert "/api/v1/observability/verification" in HTML
    assert "Claude · reference specification" in HTML
    assert "Manus · independent specification" in HTML
