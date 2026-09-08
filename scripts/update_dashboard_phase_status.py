from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('Next lane: swing research specification pending; no swing signal is shown. A future family requires its own preregistered hypothesis, costs, OOS split, and acceptance gate.', 'H-SW1 legacy verification is available only through the explicit read-only comparison action. No swing method is promoted; a future overlap method requires its own preregistration, costs, OOS split, and acceptance gate.')
p.write_text(s,encoding='utf-8')
print('dashboard phase status updated')
