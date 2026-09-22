-- Historical dataset control-plane registry.
-- Raw historical payloads stay outside Supabase when practical.

create table if not exists public.research_dataset_registry (
  dataset_id text primary key,
  source_type text not null,
  source_uri text not null,
  source_name text,
  symbol text,
  timeframe text,
  start_time_ms bigint,
  end_time_ms bigint,
  storage_class text not null default 'EXTERNAL_ARCHIVE',
  storage_uri text,
  sha256 text,
  byte_size bigint,
  provenance_status text not null default 'UNVERIFIED',
  redistributable_status text not null default 'UNKNOWN',
  immutable boolean not null default true,
  notes text,
  created_at timestamptz not null default now()
);

alter table public.research_dataset_registry enable row level security;

drop policy if exists "research_dataset_registry_no_public_read"
  on public.research_dataset_registry;

create index if not exists idx_research_dataset_registry_symbol_time
  on public.research_dataset_registry(symbol, timeframe, start_time_ms);

create index if not exists idx_research_dataset_registry_source
  on public.research_dataset_registry(source_type);

create or replace function public.prevent_dataset_registry_mutation()
returns trigger
language plpgsql
as $$
begin
  raise exception 'research_dataset_registry is append-only; corrections require a new dataset_id/version';
end;
$$;

drop trigger if exists trg_prevent_dataset_registry_mutation
  on public.research_dataset_registry;

create trigger trg_prevent_dataset_registry_mutation
before update or delete on public.research_dataset_registry
for each row execute function public.prevent_dataset_registry_mutation();
