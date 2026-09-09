from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
old="$('chartLine').setAttribute('d','M '+pts.map((p,i)=>{const [x,y]=p.split(',');return (i?'L ':'M ')+(70+Number(x)*810/900)+','+y}).join(' '));$('chartArea').setAttribute('d','M '+pts.map((p,i)=>{const [x,y]=p.split(',');return (i?'L ':'M ')+(70+Number(x)*810/900)+','+y}).join(' ')+' L 880,230 L 70,230 Z');"
new="$('chartLine').setAttribute('d',pts.map((p,i)=>{const [x,y]=p.split(',');return (i?'L ':'M ')+(70+Number(x)*810/900)+','+y}).join(' '));$('chartArea').setAttribute('d',pts.map((p,i)=>{const [x,y]=p.split(',');return (i?'L ':'M ')+(70+Number(x)*810/900)+','+y}).join(' ')+' L 880,230 L 70,230 Z');"
if old not in s: raise SystemExit('SVG path prefix sequence not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('SVG path prefix fixed')
