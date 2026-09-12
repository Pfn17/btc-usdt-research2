from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")
assert "H-VOL1 · Breakout" not in html

anchor = '<div class="research-block"><div class="lineage-grid">'
assert anchor in html
card = '''<div class="research-block"><article class="research-card"><div class="research-head"><div><div class="research-name">H-VOL1 · Breakout with taker-flow confirmation</div><div class="research-kind">New OHLCV hypothesis · readiness only · outcome not run</div></div><div id="hvol1Status" class="state-pill gold">IMPLEMENTED · AWAITING AUDIT</div></div><div class="metrics"><div class="metric"><small>Implementation status</small><b id="hvol1Implementation">IMPLEMENTED</b></div><div class="metric"><small>Data source</small><b id="hvol1Data">OHLCV · 1m</b></div><div class="metric wide"><small>1-minute continuity / detected gaps</small><b id="hvol1Coverage">NOT YET COMPUTED</b></div><div class="metric wide"><small>Complete 120-minute range windows</small><b id="hvol1Range">NOT YET COMPUTED</b></div><div class="metric"><small>Valid taker-ratio observations</small><b id="hvol1Ratio">NOT YET COMPUTED</b></div><div class="metric"><small>Training period</small><b id="hvol1Training">NOT YET COMPUTED</b></div><div class="metric"><small>Potential OOS period</small><b id="hvol1Oos">NOT YET COMPUTED</b></div><div class="metric"><small>Training P90</small><b id="hvol1P90">NOT YET FROZEN</b></div><div class="metric"><small>Training P10</small><b id="hvol1P10">NOT YET FROZEN</b></div><div class="metric wide"><small>Exact OOS boundary</small><b id="hvol1Boundary">NOT FROZEN</b></div><div class="metric"><small>Entry-candle availability</small><b id="hvol1Entry">NOT YET COMPUTED</b></div><div class="metric"><small>120-minute exit availability</small><b id="hvol1Exit">NOT YET COMPUTED</b></div><div class="metric wide"><small>Non-overlap methodology</small><b id="hvol1NonOverlap">GREEDY · PREVIOUS ACCEPTED EXIT</b></div><div class="metric"><small>Baseline cost</small><b id="hvol1Baseline">10 bps RT</b></div><div class="metric"><small>Stress cost</small><b id="hvol1Stress">12 bps RT</b></div><div class="metric wide"><small>Outcome status</small><b id="hvol1Outcome">UNRUN</b></div><div class="metric wide"><small>Authorization status</small><b id="hvol1Authorization">NOT GRANTED</b></div></div><div class="research-explain"><strong>Research boundary:</strong> H-VOL1 tests a 120-minute breakout only when taker-buy participation confirms direction. Readiness is visible from persisted OHLCV facts; the dashboard does not choose an OOS cutoff, preview profitability, or execute the outcome scan.</div></article></div>
'''
html = html.replace(anchor, card + anchor, 1)

old_fn = "function renderHfb3(p){const x=row(p);"
assert old_fn in html
readiness_fn = "function renderHvol1Readiness(p){const x=p?.data||p;if(!x){['hvol1Coverage','hvol1Range','hvol1Ratio','hvol1Training','hvol1Oos','hvol1P90','hvol1P10','hvol1Entry','hvol1Exit'].forEach(id=>set(id,'UNAVAILABLE'));return}set('hvol1Status',x.status||'IMPLEMENTED · AWAITING AUDIT');set('hvol1Coverage',fmt(x.candle_count,0)+' candles · '+fmt(x.missing_minute_count,0)+' gaps · '+(x.continuity_ok?'CONTINUOUS':'GAPS DETECTED'));set('hvol1Range',fmt(x.complete_range_window_count,0)+' complete windows');set('hvol1Ratio',fmt(x.valid_taker_ratio_count,0));set('hvol1Training',x.training_candles==null?'NOT YET COMPUTED':fmt(x.training_candles,0)+' candles');set('hvol1Oos',x.oos_candles==null?'NOT YET COMPUTED':fmt(x.oos_candles,0)+' candles');set('hvol1P90',x.training_p90==null?'NOT YET FROZEN':fmt(x.training_p90,6));set('hvol1P10',x.training_p10==null?'NOT YET FROZEN':fmt(x.training_p10,6));set('hvol1Boundary',x.oos_boundary_frozen?'FROZEN':'NOT FROZEN');set('hvol1Entry',fmt(x.entry_available_count,0));set('hvol1Exit',fmt(x.exit_available_count,0));set('hvol1NonOverlap',x.non_overlap_method||'UNAVAILABLE');set('hvol1Baseline',x.baseline_cost_bps==null?'UNAVAILABLE':fmt(x.baseline_cost_bps,0)+' bps RT');set('hvol1Stress',x.stress_cost_bps==null?'UNAVAILABLE':fmt(x.stress_cost_bps,0)+' bps RT');set('hvol1Outcome',x.outcome_run?'RUN':'UNRUN');set('hvol1Authorization',x.authorization||'NOT GRANTED')}\n"
html = html.replace(old_fn, readiness_fn + old_fn, 1)

old_load = "async function loadResearch(){const [a,h3,b,c,readiness]=await Promise.all([safe('/api/v1/research/hfb1'),safe('/api/v1/research/hfb3'),safe('/api/v1/research/sw1-claude'),safe('/api/v1/research/sw1-manus'),safe('/api/v1/research/hmr1/readiness')]);data={hfb:a,hfb3:h3,ref:b,ind:c};const rd=readiness?.data;"
assert old_load in html
new_load = "async function loadResearch(){const [a,h3,b,c,readiness,hvolReadiness]=await Promise.all([safe('/api/v1/research/hfb1'),safe('/api/v1/research/hfb3'),safe('/api/v1/research/sw1-claude'),safe('/api/v1/research/sw1-manus'),safe('/api/v1/research/hmr1/readiness'),safe('/api/v1/research/hvol1/readiness')]);data={hfb:a,hfb3:h3,ref:b,ind:c};renderHvol1Readiness(hvolReadiness);const rd=readiness?.data;"
html = html.replace(old_load, new_load, 1)

old_return = "return Boolean(a&&h3&&b&&c)}"
assert old_return in html
html = html.replace(old_return, "return Boolean(a&&h3&&b&&c&&readiness&&hvolReadiness)}", 1)
path.write_text(html, encoding="utf-8")
print(f"patched {path}")
