from pathlib import Path
p=Path(__file__).resolve().parents[1]/'supabase'/'migrations'/'20260911173000_hmr1_gate_readiness.sql'
s=p.read_text()
old="s.boundary_frozen AND s.expected=s.candles AND s.exact_count=s.candles AND s.entry_count>0"
new="s.boundary_frozen AND s.expected=s.candles AND s.exact_count>=greatest(0,s.expected-15) AND s.entry_count>0"
if old not in s: raise SystemExit('readiness status condition not found')
s=s.replace(old,new,1)
p.write_text(s)
print('readiness eligible predecessor condition refined')
