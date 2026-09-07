from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")

# Native editorial typography and restrained institutional surfaces.
html = html.replace(
    ':root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;',
    ':root{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Inter","Helvetica Neue",Arial,sans-serif;font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1,"zero" 1;'
)
html = html.replace(
    'border-radius:17px;box-shadow:var(--shadow)',
    'border-radius:12px;box-shadow:0 14px 38px #0003'
)
html = html.replace(
    '.title{font-size:20px;font-weight:850;',
    '.title{font-size:19px;font-weight:780;'
)
html = html.replace(
    '.hero h1{margin:0;font-size:clamp(28px,4vw,44px);',
    '.hero h1{margin:0;font-size:clamp(30px,4vw,46px);font-weight:780;'
)
css_anchor = '.footnote{margin-top:10px;color:var(--faint);font-size:11px}'
css_add = '.archive-tabs{display:flex;gap:7px;margin:0 0 24px;padding:4px;border:1px solid var(--line);border-radius:10px;background:#0a1220;width:max-content}.archive-tab{border:0;border-radius:7px;background:transparent;color:var(--muted);font:inherit;font-size:11px;font-weight:760;letter-spacing:.04em;padding:8px 13px;cursor:pointer}.archive-tab:hover{color:#edf3ff}.archive-tab.active{color:#07121c;background:var(--cyan);box-shadow:0 0 18px #67e8f926}.archive-panel{transition:opacity .22s ease,transform .22s ease}.archive-panel.is-muted{opacity:.42}.utc-clock{color:var(--muted);font-size:10px;letter-spacing:.08em;white-space:nowrap}.exec-badge{display:inline-flex;align-items:center;gap:6px;color:#fda4af;font-size:10px;font-weight:800;letter-spacing:.1em}.exec-badge:before{content:"";width:6px;height:6px;border-radius:50%;background:var(--red)}.updated{animation:value-flash .65s ease}.section[data-panel]{scroll-margin-top:90px}.section[data-panel] .panel-tag{color:var(--faint);font-size:10px;font-weight:650;letter-spacing:.08em}@keyframes value-flash{0%{color:var(--cyan);text-shadow:0 0 18px #67e8f966}100%{color:inherit;text-shadow:none}}@media(max-width:620px){.archive-tabs{width:100%;justify-content:space-between}.archive-tab{flex:1;padding:8px 5px}.utc-clock{display:none}}'
if css_anchor not in html:
    raise SystemExit("css anchor missing")
html = html.replace(css_anchor, css_anchor + css_add, 1)

# Minimal static favicon: H mark + observation dot, no external asset/request.
favicon = '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 rx=%2714%27 fill=%27%23070b16%27/%3E%3Cpath d=%27M17 15v34M47 15v34M17 32h30%27 stroke=%27%2367e8f9%27 stroke-width=%276%27 stroke-linecap=%27round%27/%3E%3Ccircle cx=%2747%27 cy=%2715%27 r=%274%27 fill=%27%23f8fafc%27/%3E%3C/svg%3E">'
html = html.replace('<title>HyperHan Lab · Research Archive</title>', '<title>HyperHan Lab · Research Archive</title>' + favicon, 1)

old_header = '<div class="status"><span class="dot" id="dot"></span><span id="status">LIVE EVIDENCE · LOADING</span></div>'
new_header = '<div style="display:flex;align-items:center;gap:18px"><span class="utc-clock" id="utcClock">UTC —</span><span class="exec-badge">EXECUTION OFF</span><div class="status"><span class="dot" id="dot"></span><span id="status">LIVE EVIDENCE · LOADING</span></div></div>'
if old_header not in html:
    raise SystemExit("header status missing")
html = html.replace(old_header, new_header, 1)

hero_end = '<div class="readonly">AUTO REFRESH<br><strong>15 seconds</strong></div></section>'
hero_new = '<div class="readonly"><span class="utc-clock">READ-ONLY ARCHIVE</span><br><strong>AUTO REFRESH · 15s</strong></div></section><nav class="archive-tabs" aria-label="Archive sections"><button class="archive-tab active" data-tab="overview" type="button">Overview</button><button class="archive-tab" data-tab="evidence" type="button">Evidence</button><button class="archive-tab" data-tab="system" type="button">System</button></nav>'
if hero_end not in html:
    raise SystemExit("hero end missing")
html = html.replace(hero_end, hero_new, 1)

# Local-only tab boundaries.
html = html.replace('<div class="grid">', '<div class="grid archive-panel" data-content="overview">', 1)
html = html.replace('<div class="section">H-FB1 research result</div>', '<div class="section" data-panel="evidence">H-FB1 post-mortem record <span class="panel-tag">FAILED RESEARCH</span></div>', 1)
html = html.replace('<section class="card full"><div class="notice"><span>●</span><div>Frozen H-FB1 result request.', '<section class="card full archive-panel" data-content="evidence"><div class="notice"><span>●</span><div>Frozen H-FB1 result request.', 1)
html = html.replace('<div class="section">Captured H-FB1 observation log</div>', '<div class="section" data-panel="evidence">Captured observation log <span class="panel-tag">AUDIT TRAIL</span></div>', 1)
# The observation log card immediately follows this heading.
log_anchor = '<section class="card full"><div class="notice"><span>●</span><div>Every non-zero completed funding event'
if log_anchor not in html:
    raise SystemExit("log section missing")
html = html.replace(log_anchor, '<section class="card full archive-panel" data-content="evidence"><div class="notice"><span>●</span><div>Every non-zero completed funding event', 1)
html = html.replace('<div class="section">System health</div>', '<div class="section" data-panel="system">System health <span class="panel-tag">RUNTIME OBSERVABILITY</span></div>', 1)
# The system card follows this heading.
sys_anchor = '<section class="card full"><div class="table-wrap"><table class="table health">'
if sys_anchor not in html:
    raise SystemExit("system section missing")
html = html.replace(sys_anchor, '<section class="card full archive-panel" data-content="system"><div class="table-wrap"><table class="table health">', 1)

# Add local interactions and smooth refresh highlighting.
js_anchor = "function iso(ms){return ms?new Date(Number(ms)).toISOString().replace('T',' ').replace('.000Z',' UTC'):'—'}"
js_add = '''function updateClock(){const now=new Date();$('utcClock').textContent='UTC '+now.toISOString().slice(11,19)}
function flash(id,next){const el=$(id);if(!el)return;const value=String(next);if(el.textContent!==value){el.classList.remove('updated');void el.offsetWidth;el.classList.add('updated')}el.textContent=next}
function setupTabs(){document.querySelectorAll('.archive-tab').forEach(tab=>tab.addEventListener('click',()=>{const selected=tab.dataset.tab;document.querySelectorAll('.archive-tab').forEach(x=>x.classList.toggle('active',x===tab));document.querySelectorAll('[data-content]').forEach(panel=>panel.classList.toggle('is-muted',selected!=='overview'&&panel.dataset.content!==selected));document.querySelectorAll('[data-panel]').forEach(heading=>heading.style.opacity=(selected==='overview'||heading.dataset.panel===selected)?'1':'.48')}))}'''
if js_anchor not in html:
    raise SystemExit("JS anchor missing")
html = html.replace(js_anchor, js_anchor + js_add, 1)
# Replace key live value assignments with flash helper.
for old, new in [
    ("$('price').textContent=fmt(c.close,2);", "flash('price',fmt(c.close,2));"),
    ("$('data').textContent=h.status==='ok'?'HEALTHY':'DEGRADED';", "flash('data',h.status==='ok'?'HEALTHY':'DEGRADED');"),
    ("$('status').textContent=h.status==='ok'?'LIVE EVIDENCE · HEALTHY':'LIVE EVIDENCE · DEGRADED';", "flash('status',h.status==='ok'?'LIVE EVIDENCE · HEALTHY':'LIVE EVIDENCE · DEGRADED');"),
]:
    if old not in html:
        raise SystemExit(f"live assignment missing: {old}")
    html = html.replace(old, new, 1)
html = html.replace("load();setInterval(load,15000);", "setupTabs();updateClock();setInterval(updateClock,1000);load();setInterval(load,15000);", 1)
path.write_text(html, encoding="utf-8")
print("quant archive UI applied")
