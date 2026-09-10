from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'dashboard' / 'index.html').read_text(encoding='utf-8')
checks = {
    'manual_research_button': 'Read frozen comparison' in html,
    'frozen_research_loader': 'loadFrozen' in html,
    'operational_timer': 'setInterval(loadTerminal,15000)' in html,
    'no_hfb1_in_operational_batch': 'get(\'/api/v1/research/hfb1\')' not in html.split('async function loadTerminal', 1)[0],
    'no_fabricated_fallback': 'no value fabricated' in html,
    'unavailable_state': 'UNAVAILABLE' in html and 'STALE' in html,
    'verification_endpoint': '/api/v1/observability/verification' in html,
    'lineage_labels': 'Claude · reference specification' in html and 'Manus · independent specification' in html,
    'archive_identity': 'Research Archive' in html,
}
for name, ok in checks.items():
    print(f'{name}={"OK" if ok else "FAIL"}')
if not all(checks.values()):
    raise SystemExit(1)
