from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")
css_anchor = ".footnote{margin-top:10px;color:var(--faint);font-size:11px}"
css_add = ".pulse{height:86px;width:100%;display:block}.pulse path{fill:none;stroke:var(--cyan);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}.pulse line{stroke:#263852;stroke-width:1}.pulse-dot{fill:#cbd5e1}.pulse-meta{display:flex;justify-content:space-between;margin-top:7px;color:var(--muted);font-size:11px}.pulse-note{color:var(--faint);font-size:10px;margin-top:8px}"
if css_anchor not in html:
    raise SystemExit("css anchor not found")
html = html.replace(css_anchor, css_anchor + css_add, 1)
markup_anchor = '<div class="section">H-FB1 research result</div>'
markup = '<div class="section">Live evidence pulse</div>\n<section class="card full"><svg class="pulse" id="evidencePulse" viewBox="0 0 600 86" role="img" aria-label="Recent BTCUSDT close evidence pulse"><line x1="0" y1="43" x2="600" y2="43"></line><path id="evidencePath" d=""></path><circle class="pulse-dot" id="evidenceDot" cx="0" cy="43" r="3"></circle></svg><div class="pulse-meta"><span id="pulseWindow">Awaiting backend candles</span><span id="pulseDelta">—</span></div><div class="pulse-note">Computed in the browser from the existing latest OHLCV response. No new endpoint, storage, or trading signal.</div></section>\n' + markup_anchor
if markup_anchor not in html:
    raise SystemExit("markup anchor not found")
html = html.replace(markup_anchor, markup, 1)
js_anchor = "function iso(ms){return ms?new Date(Number(ms)).toISOString().replace('T',' ').replace('.000Z',' UTC'):'—'}"
js_add = "function renderPulse(rows){const data=(rows||[]).slice().reverse().filter(x=>Number.isFinite(Number(x.close)));if(!data.length){$('pulseWindow').textContent='No backend candles';$('pulseDelta').textContent='—';$('evidencePath').setAttribute('d','');return}const values=data.map(x=>Number(x.close));const min=Math.min(...values),max=Math.max(...values),span=max-min||1;const points=values.map((v,i)=>[i*(600/Math.max(1,values.length-1)),72-((v-min)/span)*58]);$('evidencePath').setAttribute('d',points.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' '));const last=points[points.length-1];$('evidenceDot').setAttribute('cx',last[0]);$('evidenceDot').setAttribute('cy',last[1]);const delta=values.length>1?values[values.length-1]-values[0]:0;$('pulseWindow').textContent=iso(data[0].open_time_ms)+' → '+iso(data[data.length-1].open_time_ms);$('pulseDelta').textContent=(delta>=0?'+':'')+fmt(delta,2)+' close delta'}"
if js_anchor not in html:
    raise SystemExit("js anchor not found")
html = html.replace(js_anchor, js_anchor + js_add, 1)
old = "const c=(o.data||[])[0]||{};"
if old not in html:
    raise SystemExit("load candle anchor not found")
html = html.replace(old, old + "renderPulse(o.data||[]);", 1)
path.write_text(html, encoding="utf-8")
print("evidence pulse added")
