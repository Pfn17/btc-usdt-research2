from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'dashboard' / 'index.html'
s = p.read_text(encoding='utf-8')
control = '<select id="themeSelect" aria-label="Appearance"><option value="exchange">Exchange</option><option value="institutional">Institutional</option><option value="research">Research</option></select>'
anchor = '<span class="utc-clock" id="utcClock">UTC —</span>'
if 'id="themeSelect"' not in s:
    if anchor not in s:
        raise SystemExit('header anchor not found')
    s = s.replace(anchor, anchor + control, 1)
css = '''
/* Three local skins. Themes alter presentation only; no data or API behavior. */
#themeSelect{font:inherit;color:#eaecef;background:#181a20;border:1px solid #474d57;border-radius:4px;padding:7px 9px;font-size:11px;cursor:pointer}#themeSelect:focus{outline:1px solid #f0b90b;outline-offset:1px}
body[data-theme="institutional"]{--bg:#111315;--panel:#17191c;--panel-2:#202328;--line:#34383e;--line-bright:#626a73;--muted:#a8afb7;--faint:#737b84;--cyan:#d9a441;--green:#8bc34a;--red:#d95757;--amber:#d9a441;color:#e8eaed}body[data-theme="institutional"] main{max-width:1180px;padding-top:34px}body[data-theme="institutional"] .card{border-radius:2px;padding:22px}body[data-theme="institutional"] .section{font-family:Georgia,serif;font-size:16px;font-weight:600;letter-spacing:0}body[data-theme="institutional"] .hero h1{font-family:Georgia,serif;font-weight:600;letter-spacing:-.025em}body[data-theme="institutional"] .hero p{font-family:Georgia,serif;font-size:14px}body[data-theme="institutional"] .notice{border-radius:2px;background:#1a1d21}
body[data-theme="research"]{--bg:#f5f5f2;--panel:#ffffff;--panel-2:#efefeb;--line:#d9d9d2;--line-bright:#a8a8a0;--muted:#686861;--faint:#8a8a82;--cyan:#ad6b00;--green:#18794e;--red:#b42318;--amber:#ad6b00;color:#171717;color-scheme:light}body[data-theme="research"] header{background:#f5f5f2;border-bottom-color:#d9d9d2}body[data-theme="research"] .mark{background:#fff;border-color:#ad6b00}body[data-theme="research"] .title,body[data-theme="research"] .card h2,body[data-theme="research"] .section,body[data-theme="research"] .notice strong{color:#171717}body[data-theme="research"] .status,body[data-theme="research"] #themeSelect,body[data-theme="research"] .controls input,body[data-theme="research"] .controls button{color:#171717;background:#fff;border-color:#a8a8a0}body[data-theme="research"] .card{border-radius:2px;background:#fff;box-shadow:none}body[data-theme="research"] .notice{background:#f1f1ed;border-color:#d9d9d2;color:#4f4f49;border-radius:2px}body[data-theme="research"] .table th{background:#efefeb;color:#686861}body[data-theme="research"] .table td{color:#30302d;border-color:#e1e1da}body[data-theme="research"] .sub,body[data-theme="research"] .hero p,body[data-theme="research"] .meta,body[data-theme="research"] .footnote,body[data-theme="research"] .utc-clock{color:#686861}body[data-theme="research"] .price-card .value{color:#171717}body[data-theme="research"] .exec-badge{color:#b42318}@media(max-width:620px){#themeSelect{max-width:105px;padding:6px 5px}}
'''
if 'Three local skins.' not in s:
    s = s.replace('</style>', css + '</style>', 1)
runtime = """
function applyTheme(theme){const allowed=['exchange','institutional','research'];const value=allowed.includes(theme)?theme:'exchange';document.body.dataset.theme=value;const selector=document.getElementById('themeSelect');if(selector)selector.value=value;try{localStorage.setItem('hyperhan-theme',value)}catch(e){}}
applyTheme((()=>{try{return localStorage.getItem('hyperhan-theme')||'exchange'}catch(e){return 'exchange'}})());
document.getElementById('themeSelect').addEventListener('change',event=>applyTheme(event.target.value));
"""
if 'hyperhan-theme' not in s:
    marker = 'const $=id=>document.getElementById(id);'
    if marker not in s:
        raise SystemExit('runtime marker not found')
    s = s.replace(marker, marker + runtime, 1)
p.write_text(s, encoding='utf-8')
print('theme switcher added')
