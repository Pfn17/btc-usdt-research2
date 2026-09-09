from pathlib import Path
from urllib.request import urlopen

base='https://btc-usdt-research2.vercel.app'
s=urlopen(base+'/', timeout=20).read().decode()
checks=[('story','id="page-story"' in s),('terminal','id="page-terminal"' in s),('visual','id="page-visual"' in s),('anchor','href="#page-terminal"' in s),('whisker','whiskerChart' in s),('chart labels','chartMax' in s),('no tab','data-page=' not in s)]
for name,ok in checks: print(f'{name}: {"OK" if ok else "FAIL"}')
print('html_bytes:',len(s))
for path in ('/health','/api/v1/research/sw1-claude','/api/v1/research/sw1-manus'):
 try:
  with urlopen(base+path, timeout=20) as r: print(path, r.status, len(r.read()))
 except Exception as e: print(path, 'ERROR', e)
