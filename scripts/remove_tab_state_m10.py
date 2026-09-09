from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('<section id="page-story" class="page active">','<section id="page-story" class="page">')
s=s.replace('<button class="action primary" data-page="terminal">Open research record</button><button class="action" data-page="visual">Open evidence view</button>','<a class="action primary" href="#page-terminal">Open research record</a><a class="action" href="#page-visual">Open evidence view</a>')
s=s.replace("function setPage(){return} ", "")
s=s.replace(' ' + '\n', '\n')
p.write_text(s,encoding='utf-8')
print('tab state removed')
