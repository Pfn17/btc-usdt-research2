from pathlib import Path
p=Path(__file__).resolve().parents[1]/'supabase'/'migrations'/'20260911173000_hmr1_gate_readiness.sql'
s=p.read_text()
s=s.replace('WITH params AS (', 'WITH RECURSIVE params AS (', 1)
old="""rows AS (
  SELECT 'overall'::text AS bucket, 'ALL'::text AS direction, n.* FROM net n
  UNION ALL
  SELECT 'week_'||iso_year||'_W'||lpad(iso_week::text,2,'0'), 'ALL', n.* FROM net n
  UNION ALL
  SELECT 'direction'::text, n.direction, n.* FROM net n
),"""
new="""rows AS (
  SELECT 'overall'::text AS bucket, 'ALL'::text AS direction, n.trigger_ms, n.entry_ms, n.entry_price, n.exit_ms, n.exit_price, n.gross_bps, n.net_bps, n.stress_net_bps, n.iso_year, n.iso_week FROM net n
  UNION ALL
  SELECT 'week_'||iso_year||'_W'||lpad(iso_week::text,2,'0'), 'ALL', n.trigger_ms, n.entry_ms, n.entry_price, n.exit_ms, n.exit_price, n.gross_bps, n.net_bps, n.stress_net_bps, n.iso_year, n.iso_week FROM net n
  UNION ALL
  SELECT 'direction'::text, n.direction, n.trigger_ms, n.entry_ms, n.entry_price, n.exit_ms, n.exit_price, n.gross_bps, n.net_bps, n.stress_net_bps, n.iso_year, n.iso_week FROM net n
),"""
if old not in s: raise SystemExit('rows block not found')
s=s.replace(old,new)
p.write_text(s)
print('H-MR1 migration SQL corrected')
