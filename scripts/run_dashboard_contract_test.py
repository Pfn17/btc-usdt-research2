from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'dashboard' / 'index.html').read_text(encoding='utf-8')
checks = {
    'initial_loading_state': 'Loading current research data' in html and 'loading-banner' in html,
    'research_slow_loop': 'setInterval(loadResearch,900000)' in html,
    'operational_timer': 'setInterval(loadOperational,15000)' in html,
    'no_research_in_operational_batch': 'async function loadOperational' in html and "safe('/api/v1/research/hfb1')" not in html.split('async function loadOperational', 1)[1].split('async function loadResearch', 1)[0],
    'no_fabricated_fallback': 'Never inferred' in html,
    'unavailable_state': 'UNAVAILABLE' in html and 'STALE' in html,
    'governance_endpoint': '/api/v1/governance/summary' in html,
    'lineage_labels': 'Reference study' in html and 'Independent study' in html,
    'archive_identity': 'Research Archive' in html,
}
for name, ok in checks.items():
    print(f'{name}={"OK" if ok else "FAIL"}')
if not all(checks.values()):
    raise SystemExit(1)
