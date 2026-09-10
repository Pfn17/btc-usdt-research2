from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'dashboard' / 'index.html'
s = p.read_text(encoding='utf-8')

nav = '<nav class="page-nav" aria-label="Research archive sections"><a href="#page-story">Story</a><a href="#page-terminal">Terminal</a><a href="#page-visual">Visual</a></nav>'
if nav not in s:
    raise SystemExit('M12 header nav not found')
s = s.replace(nav, '', 1)

old = "['visualCandles','visualFirst','visualLast','visualChange','visualEvidenceState','visualFetched','flowApi','flowStore'].forEach(id=>$(id).textContent='UNAVAILABLE');$('flowArchive').textContent='READ-ONLY'"
new = "['visualCandles','visualFirst','visualLast','visualChange','visualEvidenceState','visualFetched'].forEach(id=>$(id).textContent='UNAVAILABLE')"
if old not in s:
    raise SystemExit('M12 Visual catch block not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('M12 precision fixes applied')
