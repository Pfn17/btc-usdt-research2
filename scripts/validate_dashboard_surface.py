from pathlib import Path
from html.parser import HTMLParser
import re

html = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
s = html.read_text(encoding="utf-8")
HTMLParser().feed(s)
assert s.count("<html") == 1 and s.count("</html>") == 1
assert "toLocaleString('en-US'" in s
for forbidden in ("radial-gradient", "linear-gradient", "Find edges.", "Tell AI", "Binance public API", "Supabase", "Railway", "Vercel"):
    assert forbidden not in s, forbidden
for required in (
    "No validated edge.", "Research archive", "Execution", "OFF", "KILL",
    "INCONCLUSIVE", "UNAVAILABLE", "Never inferred", "Loading current research data",
    "Current position", "Evidence you can inspect", "System state and provenance",
    "Reference study", "Independent study", "/api/v1/research/hfb1",
    "/api/v1/research/sw1-claude", "/api/v1/research/sw1-manus",
    "/api/v1/governance/summary", "READ-ONLY", "zero decision boundary",
):
    assert required in s, required
assert len(re.findall(r"<script>", s)) == 1
assert len(re.findall(r"</script>", s)) == 1
print(f"dashboard surface: PASS ({len(s)} bytes)")
