from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")
replacements = {
    '<meta name="description" content="HyperHan Lab Research Console · BTCUSDT Research Dashboard · read-only live market-data observability">': '<meta name="description" content="HyperHan Lab Research Archive · BTCUSDT live evidence portfolio · read-only">',
    '<title>HyperHan Lab · Research Console</title>': '<title>HyperHan Lab · Research Archive</title>',
    '<div class="title">HyperHan Lab</div><div class="sub">Research Console · systematic crypto research · read-only</div>': '<div class="title">HyperHan Lab</div><div class="sub">Research Archive · live evidence portfolio · read-only</div>',
    '<div class="status"><span class="dot" id="dot"></span><span id="status">Loading</span></div>': '<div class="status"><span class="dot" id="dot"></span><span id="status">LIVE EVIDENCE · LOADING</span></div>',
    '<p class="eyebrow">HyperHan Research Console · H-FB1</p><h1>Find edges. Reject noise.</h1><p>Real data from the research API, presented without execution or fabricated values. Funding-rate observations remain research evidence, not a trading approval.</p>': '<p class="eyebrow">HyperHan Research Archive · BTCUSDT</p><h1>No validated edge.</h1><p>Live evidence from the research system, preserved as a portfolio of work. Observations, failures, and data health are shown without turning them into trading approval.</p>',
    '<section class="card"><h2>Data pipeline</h2><div class="value" id="data">—</div><div class="meta" id="age">—</div><div class="row"><span>Session</span><strong id="session">—</strong></div></section>': '<section class="card"><h2>Evidence freshness</h2><div class="value" id="data">—</div><div class="meta" id="age">—</div><div class="row"><span>Collector session</span><strong id="session">—</strong></div></section>',
    '<section class="card signal-card"><h2>Observed funding direction</h2><div class="value" id="signal">—</div>': '<section class="card signal-card"><h2>Observed funding direction</h2><div class="value observed" id="signal">—</div>',
    '<div class="section">System map</div>\n<section class="card full"><div class="system-map" id="systemMap"><div class="diagram-node">Exchange APIs<small>checking</small></div><div class="diagram-arrow">→</div><div class="diagram-node">Collector<small>checking</small></div><div class="diagram-arrow">→</div><div class="diagram-node">Supabase → API → Console<small>checking</small></div></div><div class="footnote">Live status is derived from the existing health response. No additional polling or data source is introduced.</div></section>\n<div class="section">Research lifecycle</div>\n<section class="card full"><div class="lifecycle" id="lifecycle"><div class="diagram-node ok">Observe<small>live evidence</small></div><div class="diagram-node ok">Hypothesize<small>mechanism</small></div><div class="diagram-node ok">Preregister<small>frozen rules</small></div><div class="diagram-node ok">Test<small>cost-adjusted</small></div><div class="diagram-node warn">Verify<small>independent check</small></div><div class="diagram-node warn">Decide<small>reject / promote</small></div></div><div class="footnote">The lifecycle is a visual explanation of the research contract, not a trading signal.</div></section>\n': '',
    '<div class="controls"><label for="start">OOS START</label><input id="start" type="datetime-local"><button id="run" type="button">Refresh H-FB1 test</button></div>': '<div class="notice"><span>●</span><div>Frozen H-FB1 result request. No interactive parameter control is exposed in the archive.</div></div>',
    'HyperHan Lab · systematic crypto research by <strong>Parhan</strong>': 'HyperHan Lab · research archive by <strong>Parhan</strong>',
}
for old, new in replacements.items():
    if old not in html:
        raise SystemExit(f"expected fragment not found: {old[:80]}")
    html = html.replace(old, new, 1)
html = html.replace(".signal-card .value{color:var(--cyan)}", ".signal-card .value{color:#cbd5e1}.signal-card .observed{font-size:clamp(22px,2.5vw,29px);font-weight:750}")
html = html.replace("$('status').textContent=h.status==='ok'?'LIVE DATA HEALTHY':'DATA DEGRADED';", "$('status').textContent=h.status==='ok'?'LIVE EVIDENCE · HEALTHY':'LIVE EVIDENCE · DEGRADED';")
html = html.replace("$('signal').className='value '+(s.signal==='LONG'?'positive':s.signal==='SHORT'?'negative':'');", "$('signal').className='value observed';")
html = html.replace("renderSystemMap(h);", "")
html = html.replace("$('systemMap').innerHTML=mapNode('Backend', 'bad', 'unavailable')+'<div class=\"diagram-arrow\">→</div>'+mapNode('Console','bad','no substitute data');", "")
html = html.replace("$('run').onclick=load;load();setInterval(load,15000);", "load();setInterval(load,15000);")
path.write_text(html, encoding="utf-8")
print("archive dashboard updated")
