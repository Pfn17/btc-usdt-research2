from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('A lab for rejecting noise.', 'Evidence before narrative.')
s=s.replace('Multiple agents can inspect code, data contracts, and decisions.', 'The archive preserves code, data contracts, and decisions.')
s=s.replace('Research pace', 'Research record')
p.write_text(s,encoding='utf-8')
print('story copy cleaned')
