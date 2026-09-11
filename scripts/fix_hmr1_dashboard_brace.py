from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text()
old="$('hmr1Outcome').textContent='UNRUN'}}}"
new="$('hmr1Outcome').textContent='UNRUN'}}"
if old not in s: raise SystemExit('extra brace sequence not found')
s=s.replace(old,new,1)
p.write_text(s)
print('H-MR1 dashboard brace fixed')
