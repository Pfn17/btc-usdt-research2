from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'dashboard' / 'index.html').read_text(encoding='utf-8')
checks = {
    'manual_research_button': 'Run comparison once' in html,
    'frozen_research_loader': 'loadFrozenResearch' in html,
    'operational_timer': 'setInterval(load,15000)' in html,
    'no_hfb1_in_operational_batch': "const [h,o,s,l,f,r]" not in html,
    'no_fabricated_fallback': 'no result fabricated' in html,
    'unavailable_state': 'Method unavailable' in html,
    'archive_identity': 'Research Archive' in html,
}
for name, ok in checks.items():
    print(f'{name}={"OK" if ok else "FAIL"}')
if not all(checks.values()):
    raise SystemExit(1)
