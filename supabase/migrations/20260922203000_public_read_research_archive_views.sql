-- Public owner-facing reads for the already-created archive metadata tables.
-- No table creation, raw data import, hypothesis creation, outcome scan, or trading path.

alter table if exists public.research_dataset_registry enable row level security;
alter table if exists public.research_hypothesis_records enable row level security;

drop policy if exists research_dataset_registry_public_read on public.research_dataset_registry;
create policy research_dataset_registry_public_read
on public.research_dataset_registry
for select to anon, authenticated
using (true);

drop policy if exists research_hypothesis_records_public_read on public.research_hypothesis_records;
create policy research_hypothesis_records_public_read
on public.research_hypothesis_records
for select to anon, authenticated
using (true);

revoke insert, update, delete, truncate, references, trigger on table public.research_dataset_registry from anon, authenticated;
revoke insert, update, delete, truncate, references, trigger on table public.research_hypothesis_records from anon, authenticated;
grant select on table public.research_dataset_registry to anon, authenticated;
grant select on table public.research_hypothesis_records to anon, authenticated;

create or replace view public.research_agent_activity_public as
select task_id, owner, lane, status, claim, evidence, verified_by, verified_at, updated_at, next_action
from public.agent_coordination_log;

grant select on public.research_agent_activity_public to anon, authenticated;

comment on view public.research_agent_activity_public is 'Owner-facing read-only coordination summary; excludes write operations.';
