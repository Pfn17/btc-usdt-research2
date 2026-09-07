from pathlib import Path
import re

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")

# Remove local tabs and their non-functional dimming behavior.
html = re.sub(r'<nav class="archive-tabs".*?</nav>', '', html, count=1, flags=re.S)
html = html.replace(' class="grid archive-panel" data-content="overview"', ' class="grid"', 1)
html = html.replace(' class="card full archive-panel" data-content="evidence"', ' class="card full"')
html = html.replace(' class="card full archive-panel" data-content="system"', ' class="card full"')

# Remove the telemetry/chart section; leave the rest of the live Binance evidence archive intact.
html = re.sub(r'<div class="section">Live evidence pulse</div>\s*<section class="card full telemetry">.*?</section>\s*<div class="section" data-panel="evidence">', '<div class="section">H-FB1 post-mortem record <span class="panel-tag">FAILED RESEARCH</span></div>', html, count=1, flags=re.S)
# The previous replacement can leave the old heading duplicated; collapse it deterministically.
html = html.replace('<div class="section">H-FB1 post-mortem record <span class="panel-tag">FAILED RESEARCH</span></div>H-FB1 post-mortem record <span class="panel-tag">FAILED RESEARCH</span></div>', '<div class="section">H-FB1 post-mortem record <span class="panel-tag">FAILED RESEARCH</span></div>', 1)

# Remove CSS used only by removed tabs/chart, retain typography and value transitions.
for pattern in [
    r'\.archive-tabs\{.*?\}', r'\.archive-tab\{.*?\}', r'\.archive-tab:hover\{.*?\}',
    r'\.archive-tab\.active\{.*?\}', r'\.archive-panel\{.*?\}', r'\.archive-panel\.is-muted\{.*?\}',
    r'\.pulse\{.*?\}', r'\.pulse path\{.*?\}', r'\.pulse-area\{.*?\}', r'\.pulse-shell\{.*?\}',
    r'\.pulse-shell:after\{.*?\}', r'\.pulse line\{.*?\}', r'\.pulse-dot\{.*?\}',
    r'\.pulse-meta\{.*?\}', r'\.pulse-delta\{.*?\}', r'\.pulse-note\{.*?\}',
    r'\.telemetry\{.*?\}', r'\.telemetry:before\{.*?\}', r'\.telemetry-head\{.*?\}',
    r'\.telemetry-kicker\{.*?\}', r'\.telemetry-title\{.*?\}', r'\.telemetry-status\{.*?\}',
    r'\.telemetry-status i\{.*?\}', r'@keyframes telemetry-sweep\{.*?\}', r'@keyframes status-pulse\{.*?\}',
]:
    html = re.sub(pattern, '', html, count=1, flags=re.S)
# Remove mobile-only rules for deleted tabs/chart.
html = html.replace('@media(max-width:620px){.archive-tabs{width:100%;justify-content:space-between}.archive-tab{flex:1;padding:8px 5px}.utc-clock{display:none}}', '@media(max-width:620px){.utc-clock{display:none}}')

# Remove chart/tab functions and keep clock + smooth value flash.
html = re.sub(r'function updateClock\(\).*?function renderPulse\(rows\)\{.*?\}\n', "function updateClock(){const now=new Date();$('utcClock').textContent='UTC '+now.toISOString().slice(11,19)}\nfunction flash(id,next){const el=$(id);if(!el)return;const value=String(next);if(el.textContent!==value){el.classList.remove('updated');void el.offsetWidth;el.classList.add('updated')}el.textContent=next}\n", html, count=1, flags=re.S)
html = html.replace("const c=(o.data||[])[0]||{};renderPulse(o.data||[]);", "const c=(o.data||[])[0]||{};")
html = html.replace('setupTabs();updateClock();setInterval(updateClock,1000);load();setInterval(load,15000);', 'updateClock();setInterval(updateClock,1000);load();setInterval(load,15000);')
# Remove stale data-panel attributes and panel-tag where no longer needed, preserve section labels.
html = re.sub(r' data-panel="[^"]*"', '', html)

path.write_text(html, encoding="utf-8")
print("Binance-only archive cleanup applied")
