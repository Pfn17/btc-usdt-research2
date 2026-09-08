from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'dashboard' / 'index.html'
s = path.read_text(encoding='utf-8')
replacements = {
    'Research Archive · live evidence portfolio · read-only': 'Research Archive · market evidence · read-only',
    'HyperHan Research Archive · BTCUSDT': 'HyperHan Research Archive · BTCUSDT',
    'Swing-lite verification comparison <span class="panel-tag">TWO METHODS · READ-ONLY</span>': 'Swing-lite verification <span class="panel-tag">FROZEN STUDIES · READ-ONLY</span>',
    'H-SW1 comparison is manual and read-only.': 'Comparison is manual and read-only.',
    'Research RPCs are not part of the 15-second market refresh. Run the comparison only when you intentionally want a new frozen observation.': 'Historical studies are not part of the 15-second market refresh. Run the comparison only when you intentionally want a new frozen observation.',
    'H-SW1-CLAUDE · official method.': 'Reference specification.',
    'This panel calls the persisted Claude RPC and preserves its result lineage. It is not independently verified by this Manus session.': 'This panel shows the frozen reference study. It is research evidence only and is not a trading signal.',
    'Method identity: H-SW1-CLAUDE · official RPC name: research_sw1_scan_frozen · not a trading signal.': 'Study role: reference specification · research only · not a trading signal.',
    'H-SW1-MANUS · independent method.': 'Independent specification.',
    'This panel calls the separately named Manus RPC. Its candidate grid, unanimous funding-sign rule, and calendar-quarter grouping are not interchangeable with the official Claude result.': 'This panel shows a separately frozen study. Its candidate grid, funding-sign rule, and period grouping are not interchangeable with the reference study.',
    'Method identity: H-SW1-MANUS · independent implementation · not promoted to paper or live execution.': 'Study role: independent specification · not promoted to paper or live execution.',
    'H-SW1 legacy verification is available only through the explicit read-only comparison action.': 'Frozen swing studies are available only through the explicit read-only comparison action.',
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f'missing text anchor: {old}')
    s = s.replace(old, new)

# Binance-like neutral exchange palette: no gradients, no neon cyan, no excessive rounding or glow.
style_end = '''
/* Public archive skin: neutral exchange terminal, not an AI product surface. */
:root{font-family:Inter,Arial,Helvetica,sans-serif;color:#eaecef;background:#0b0e11;color-scheme:dark;--bg:#0b0e11;--panel:#181a20;--panel-2:#1e2329;--line:#2b3139;--line-bright:#474d57;--muted:#929aa5;--faint:#6b7280;--cyan:#f0b90b;--green:#0ecb81;--red:#f6465d;--amber:#f0b90b;--shadow:none}
body{background:#0b0e11}
header{background:#0b0e11;border-bottom:1px solid #2b3139;backdrop-filter:none}
.mark{border-color:#f0b90b;border-radius:4px;background:#181a20;color:#f0b90b;box-shadow:none}
.title{font-size:17px;font-weight:700;letter-spacing:0}
.sub{color:#929aa5}
.status{border-color:#2b3139;border-radius:4px;color:#eaecef}
.dot.ok{background:#0ecb81;box-shadow:none}.dot.bad{background:#f6465d;box-shadow:none}.dot.warn{background:#f0b90b;box-shadow:none}
main{padding-top:24px}.eyebrow{color:#f0b90b;letter-spacing:.12em}.hero h1{font-size:clamp(28px,4vw,42px);font-weight:700;letter-spacing:-.03em}.hero p{color:#929aa5}
.card{padding:18px;background:#181a20;border:1px solid #2b3139;border-radius:4px;box-shadow:none}.card h2{color:#929aa5}.price-card .value{color:#eaecef}.signal-card{background:#181a20}.signal-card .value{color:#eaecef}.positive{color:#0ecb81!important}.negative{color:#f6465d!important}
.notice{padding:13px 14px;background:#1e2329;border:1px solid #2b3139;border-radius:4px;color:#b7bdc6}.notice strong{color:#eaecef}.safety{border-color:#5b2730;background:#1e171b}.safety .value{color:#f6465d}
.section{color:#eaecef;font-size:14px;font-weight:700}.section:after{background:#2b3139}.panel-tag{color:#6b7280}
.controls input,.controls button{color:#eaecef;background:#181a20;border:1px solid #474d57;border-radius:4px}.controls button:hover{border-color:#f0b90b;color:#f0b90b}
.table-wrap{border-color:#2b3139;border-radius:4px}.table th,.table td{border-color:#2b3139}.table th{color:#6b7280;background:#1e2329}.table td{color:#d1d5db}.table tbody tr:hover{background:#1e2329}
.footnote,.meta{color:#6b7280}.utc-clock{color:#929aa5}.exec-badge{color:#f6465d}.exec-badge:before{background:#f6465d}.updated{animation:value-flash .45s ease}@keyframes value-flash{0%{color:#f0b90b}100%{color:inherit}}
''' 
s = s.replace('</style>', style_end + '</style>', 1)
path.write_text(s, encoding='utf-8')
print('public dashboard brand cleaned')
