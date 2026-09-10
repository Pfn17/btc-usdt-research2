from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard/index.html").read_text(encoding="utf-8")


def test_research_rpcs_are_slow_and_not_on_operational_timer():
    assert "loadResearch" in HTML
    assert "setInterval(loadOperational,15000)" in HTML
    assert "setInterval(loadResearch,900000)" in HTML
    assert "safe('/api/v1/research/hfb1')" in HTML
    assert "safe('/api/v1/research/sw1-claude')" in HTML
    assert "safe('/api/v1/research/sw1-manus')" in HTML


def test_owner_visibility_and_no_fabrication_boundary():
    assert "Never inferred" in HTML
    assert "Execution" in HTML and "OFF" in HTML
    assert "Some current data could not be retrieved" in HTML
    assert "RESEARCH ARCHIVE" in HTML
    assert "UNAVAILABLE" in HTML
    assert "STALE" in HTML
    assert "/api/v1/governance/summary" not in HTML
    assert "Reference lineage" in HTML
    assert "Independent lineage" in HTML
    assert "Loading current research data" in HTML
    assert "Project memory" not in HTML
    assert "Owner direction" not in HTML
