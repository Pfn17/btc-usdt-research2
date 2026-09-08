from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")


def test_research_rpcs_are_not_on_operational_timer():
    assert "Run comparison once" in HTML
    assert "loadFrozenResearch" in HTML
    assert "setInterval(load,15000)" in HTML
    assert "const [h,o,s,l,f]" in HTML
    assert "const [h,o,s,l,f,r]" not in HTML


def test_owner_visibility_and_no_fabrication_boundary():
    assert "no result fabricated" in HTML
    assert "trading_enabled" not in HTML or "EXECUTION OFF" in HTML
    assert "Method unavailable" in HTML
    assert "Research Archive" in HTML
