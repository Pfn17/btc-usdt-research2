from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace("(Number(x)+70)+','+y", "(70+Number(x)*810/900)+','+y")
s=s.replace("function renderWhiskers(){if(!$('whiskerRows'))return;$('whiskerRows').innerHTML=whiskerPoint(55,'H-FB1',researchPayloads.hfb,'bad')+whiskerPoint(95,'H-SW1 overall',researchPayloads.sw1Ref,'warn')+whiskerPoint(135,'H-SW1 independent',researchPayloads.sw1Ind,'warn')+`<text class=\\\"whisker-text\\\" x=\\\"10\\\" y=\\\"175\\\">H-SW1 quarter</text><text class=\\\"whisker-value\\\" x=\\\"250\\\" y=\\\"175\\\">SEE TERMINAL BREAKDOWN</text>`}", "function renderWhiskers(){if(!$('whiskerRows'))return;const ref=(researchPayloads.sw1Ref?.data||[]).filter(x=>x.bucket&&x.bucket!=='overall').slice(0,4);const rows=[whiskerPoint(55,'H-FB1',researchPayloads.hfb,'bad'),whiskerPoint(95,'H-SW1 overall',researchPayloads.sw1Ref,'warn'),whiskerPoint(135,'H-SW1 independent',researchPayloads.sw1Ind,'warn')];ref.forEach((x,i)=>rows.push(whiskerPoint(175+i*30,x.bucket,{data:[x]},'warn')));$('whiskerRows').innerHTML=rows.join('');$('whiskerChart').setAttribute('viewBox',`0 0 900 ${Math.max(250,190+ref.length*30)}`)}")
p.write_text(s,encoding='utf-8')
print('M10 visual refinement applied')
