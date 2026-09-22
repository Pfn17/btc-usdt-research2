-- Canonical immutable hypothesis memory
create table if not exists public.research_hypothesis_records (
  hypothesis_id text not null,
  record_version integer not null default 1,
  title text not null,
  family text,
  status text not null,
  origin_type text not null,
  origin_source text,
  origin_reference text,
  research_question text,
  rationale text,
  mechanism text,
  variables jsonb not null default '{}'::jsonb,
  equations jsonb not null default '{}'::jsonb,
  frozen_parameters jsonb not null default '{}'::jsonb,
  entry_exit_rules jsonb not null default '{}'::jsonb,
  cost_model jsonb not null default '{}'::jsonb,
  validation_contract jsonb not null default '{}'::jsonb,
  lineage jsonb not null default '{}'::jsonb,
  decision jsonb not null default '{}'::jsonb,
  provenance_status text not null,
  source_documents text[] not null default '{}',
  created_at timestamptz not null default now(),
  primary key (hypothesis_id, record_version)
);

comment on table public.research_hypothesis_records is
'Canonical immutable memory for research hypotheses: origin, rationale, mechanism, equations, frozen rules, validation contract, lineage and decision. Dashboard is a view, not the source of truth.';

alter table public.research_hypothesis_records enable row level security;

create or replace function public.prevent_hypothesis_record_mutation()
returns trigger
language plpgsql
as $$
begin
  raise exception 'research_hypothesis_records is append-only; create a new record_version';
end;
$$;

drop trigger if exists trg_research_hypothesis_records_immutable on public.research_hypothesis_records;
create trigger trg_research_hypothesis_records_immutable
before update or delete on public.research_hypothesis_records
for each row execute function public.prevent_hypothesis_record_mutation();

create index if not exists idx_research_hypothesis_records_status
on public.research_hypothesis_records(status);

create index if not exists idx_research_hypothesis_records_family
on public.research_hypothesis_records(family);
