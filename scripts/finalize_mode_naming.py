from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8').replace("allowed.includes(theme)?theme:'exchange'", "allowed.includes(theme)?theme:'terminal'").replace("return 'exchange'", "return 'terminal'")
p.write_text(s,encoding='utf-8')
cp=root/'docs'/'SYNC_CHECKPOINT_2026-09-09.md'
if cp.exists():
    t=cp.read_text(encoding='utf-8').replace('Terminal, Apple, Story / Visual','Terminal, Clean, Story').replace('Terminal, Apple, and Story / Visual','Terminal, Clean, and Story').replace('historical draft wording; superseded by the three final labels Terminal, Apple, and Story / Visual.','historical draft wording; superseded by the three final labels Terminal, Clean, and Story.')
    cp.write_text(t,encoding='utf-8')
print('mode naming finalized')
