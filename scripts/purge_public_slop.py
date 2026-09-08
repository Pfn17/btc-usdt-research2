from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / 'dashboard' / 'index.html'
s = p.read_text(encoding='utf-8')
# Remove stale visual declarations from the original skin so public source and rendered style agree.
s = re.sub(r'background:radial-gradient\([^;]+\),var\(--bg\)', 'background:var(--bg)', s)
s = re.sub(r'background:linear-gradient\([^;]+\)', 'background:var(--panel)', s)
s = s.replace('font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Inter","Helvetica Neue",Arial,sans-serif', 'font-family:Inter,Arial,Helvetica,sans-serif')
s = s.replace('box-shadow:0 0 28px #22d3ee20', 'box-shadow:none')
s = s.replace('box-shadow:0 14px 38px #0003', 'box-shadow:none')
s = s.replace('box-shadow:0 20px 55px #0005', 'box-shadow:none')
s = s.replace('--cyan:#67e8f9', '--cyan:#f0b90b')
# Keep only neutral public labels in visible markup.
s = s.replace('const [claude,manus]=await Promise.all([get(\'/api/v1/research/sw1-claude\'),get(\'/api/v1/research/sw1-manus\')]);', "const [reference,independent]=await Promise.all([get('/api/v1/research/sw1-claude'),get('/api/v1/research/sw1-manus')]);")
s = s.replace("renderSw1Overall('sw1ClaudeOverall',claude);const rows=renderSw1Overall('sw1ManusOverall',manus);", "renderSw1Overall('sw1ClaudeOverall',reference);const rows=renderSw1Overall('sw1ManusOverall',independent);")
p.write_text(s, encoding='utf-8')
print('public slop purged')
