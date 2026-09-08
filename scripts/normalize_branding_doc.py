from pathlib import Path
p=Path(__file__).resolve().parents[1]/'docs'/'BRANDING.md'
p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
print('branding normalized')
