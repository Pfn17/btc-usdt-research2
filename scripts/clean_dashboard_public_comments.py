from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8').replace('/* Public archive skin: neutral exchange terminal, not an AI product surface. */','/* Public archive skin: neutral exchange terminal. */')
p.write_text(s,encoding='utf-8')
print('public comments cleaned')
