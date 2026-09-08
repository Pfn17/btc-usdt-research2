from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
for old,new in {
    'sw1ClaudeOverall':'studyReferenceOverall',
    'sw1ManusOverall':'studyIndependentOverall',
    'sw1ManusQuarters':'studyIndependentPeriods',
    'No Manus quarter data':'No independent study period data',
}.items():
    s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('dashboard DOM names neutralized')
