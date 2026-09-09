from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace("$('terminalFetched').textContent=now();renderResult('hfb',r)", "$('terminalFetched').textContent=now();renderResult('hfb',r);renderWhiskers()")
s=s.replace("$('runSw1').addEventListener('click',loadFrozen);loadPage();terminalTimer=", "$('runSw1').addEventListener('click',loadFrozen);loadPage();loadFrozen();terminalTimer=")
p.write_text(s,encoding='utf-8')
print('initial research read enabled')
