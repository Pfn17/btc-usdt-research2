from pathlib import Path
from html.parser import HTMLParser
import re

html = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
s = html.read_text(encoding="utf-8")
HTMLParser().feed(s)
assert s.count("<html") == 1 and s.count("</html>") == 1
assert "toLocaleString('en-US'" in s
for forbidden in ("radial-gradient", "linear-gradient", "Find edges.", "Tell AI", "Binance public API", "Supabase", "Railway", "Vercel", "Project memory", "Owner direction", "/api/v1/governance/summary"):
    assert forbidden not in s, forbidden
for required in (
    "No validated edge", "Research Archive", "Execution", "OFF", "KILL",
    "UNAVAILABLE", "backend-derived", "owner-frozen boundary",
    "Owner-frozen evaluation", "H-MR1", "H-VOL1",
    "/api/v1/research/hmr1", "/api/v1/research/hvol1",
    "Training P90", "Contamination handling", "Independent verifier separate from executor",
):
    assert required in s, required
assert len(re.findall(r"<script>", s)) == 1
assert len(re.findall(r"</script>", s)) == 1
print(f"dashboard surface: PASS ({len(s)} bytes)")
