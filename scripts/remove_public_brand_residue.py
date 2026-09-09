from pathlib import Path
root=Path(__file__).resolve().parents[1]
for rel in ['dashboard/index.html','scripts/rebuild_dashboard_three_pages.py']:
    p=root/rel
    s=p.read_text(encoding='utf-8').replace('-apple-system,','')
    p.write_text(s,encoding='utf-8')
print('public brand residue removed')
