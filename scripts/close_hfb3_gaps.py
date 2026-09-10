from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")

old_stress = "const evidence=p.evidence||{},params=evidence.parameters||{},weekly=evidence.regime_stability||{};"
new_stress = "const evidence=p.evidence||{},weekly=evidence.regime_stability||{};"
assert old_stress in html, "H-FB3 render function changed; inspect before patching"
html = html.replace(old_stress, new_stress, 1)
old_value = "set('hfb3Stress',params.stress_rt_bps?fmt(Number(x.mean_net_bps)-2)+' bps':'UNAVAILABLE');"
new_value = "set('hfb3Stress',evidence.stress_net_bps==null?'UNAVAILABLE':fmt(Number(evidence.stress_net_bps))+' bps');"
assert old_value in html, "H-FB3 stress bug target not found"
html = html.replace(old_value, new_value, 1)

old_row = '<div class="ev-row"><div class="ev-label">Funding study</div><div class="ev-track"><i class="ev-zero"></i><i id="hfbRange" class="ev-range red"></i><i id="hfbPoint" class="ev-point red"></i></div><div id="hfbEvLabel" class="ev-value">LOADING</div></div>'
new_row = old_row + '<div class="ev-row"><div class="ev-label">H-FB3 · closed-range</div><div class="ev-track"><i class="ev-zero"></i><i id="hfb3Range" class="ev-range red"></i><i id="hfb3Point" class="ev-point red"></i></div><div id="hfb3EvLabel" class="ev-value">LOADING</div></div>'
assert old_row in html, "EV chart funding row target not found"
assert 'id="hfb3Range"' not in html
html = html.replace(old_row, new_row, 1)

old_items = "const items=[['hfbRange','hfbPoint','hfbEvLabel',data.hfb],['refRange','refPoint','refEvLabel',data.ref],['indRange','indPoint','indEvLabel',data.ind]];"
new_items = "const items=[['hfbRange','hfbPoint','hfbEvLabel',data.hfb],['hfb3Range','hfb3Point','hfb3EvLabel',data.hfb3],['refRange','refPoint','refEvLabel',data.ref],['indRange','indPoint','indEvLabel',data.ind]];"
assert old_items in html, "EV chart item list target not found"
html = html.replace(old_items, new_items, 1)

path.write_text(html, encoding="utf-8")
print("patched", path)
