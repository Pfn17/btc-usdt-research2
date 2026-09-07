from pathlib import Path
import re

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")
# Remove stale rules left by the first conservative cleanup pass.
for token in [
    r'\.section\[data-panel\]\{[^}]*\}',
    r'\.section\[data-panel\] \.panel-tag\{[^}]*\}',
    r'@keyframes telemetry-sweep\{.*?\}',
    r'@keyframes status-pulse\{.*?\}',
    r'@media\(max-width:620px\)\{\.telemetry\{.*?\.pulse-shell\{height:122px\}\}',
]:
    html = re.sub(token, '', html, count=1, flags=re.S)
path.write_text(html, encoding="utf-8")
print("stale removed UI CSS purged")
