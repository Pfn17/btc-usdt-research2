create table if not exists public.research_lineage_manifest (
  id bigint generated always as identity primary key,
  hypothesis_key text not null,
  result_id uuid,
  canonical_function text not null,
  canonical_signature text not null,
  preregistration_path text,
  migration_refs jsonb not null default '[]'::jsonb,
  code_version text,
  dataset_hash text,
  replay_status text not null check (replay_status in ('MATCH','MISMATCH','NOT_REPLAYED')),
  replay_notes text,
  verifier text,
  verified_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);
create table if not exists public.executable_pnl_contract (
  id bigint generated always as identity primary key,
  contract_version text not null unique,
  symbol text not null default 'BTCUSDT',
  decision_timestamp_rule text not null,
  entry_price_rule text not null,
  exit_price_rule text not null,
  fee_bps_per_side numeric not null,
  slippage_bps_per_side numeric not null,
  baseline_round_trip_bps numeric not null,
  stress_round_trip_bps numeric not null,
  latency_rule text not null,
  funding_rule text not null,
  overlap_rule text not null,
  missing_data_rule text not null,
  promotion_time_rule text not null,
  trading_authorization text not null default 'OFF',
  frozen_at timestamptz not null default now()
);
create table if not exists public.research_regression_gate (
  id bigint generated always as identity primary key,
  run_id text not null,
  test_name text not null,
  expected text not null,
  observed text not null,
  pass boolean not null,
  evidence jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
alter table public.research_lineage_manifest enable row level security;
alter table public.executable_pnl_contract enable row level security;
alter table public.research_regression_gate enable row level security;
