from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tests'/'test_dashboard.py'
s=p.read_text(encoding='utf-8').replace('"#F0B90B"','"#f0b90b"').replace('"#181A20"','"#181a20"')
p.write_text(s,encoding='utf-8')
print('test tokens updated')
