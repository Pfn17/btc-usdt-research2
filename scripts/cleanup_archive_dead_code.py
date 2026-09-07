from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
html = path.read_text(encoding="utf-8")
css = '.system-map,.lifecycle{display:grid;gap:9px;align-items:center}.system-map{grid-template-columns:repeat(5,1fr)}.lifecycle{grid-template-columns:repeat(6,1fr)}.diagram-node{min-width:0;padding:13px 9px;text-align:center;border:1px solid var(--line-bright);border-radius:12px;background:#111c30;font-size:11px;font-weight:800}.diagram-node small{display:block;margin-top:5px;color:var(--muted);font-size:10px;font-weight:600}.diagram-arrow{text-align:center;color:var(--indigo);font-weight:900}.diagram-node.ok{border-color:#26734c;background:#102b27}.diagram-node.warn{border-color:#80631f;background:#2b2412}.diagram-node.bad{border-color:#703943;background:#291821}@media(max-width:760px){.system-map,.lifecycle{grid-template-columns:1fr}.diagram-arrow{transform:rotate(90deg)}}\n'
if css not in html:
    raise SystemExit("diagram css not found")
html = html.replace(css, "", 1)
start = html.find('function mapNode(')
end = html.find('async function load()', start)
if start < 0 or end < 0:
    raise SystemExit("diagram JS functions not found")
html = html[:start] + html[end:]
path.write_text(html, encoding="utf-8")
print("dead diagram code removed")
