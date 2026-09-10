-- Durable owner authority and agent recommendation memory.
-- Public clients may read the bounded, non-sensitive archive; writes remain trusted/admin only.
create table if not exists public.owner_decisions (
  id bigint generated always as identity primary key,
  decision_type text not null,
  title text not null,
  decision text not null,
  owner_reason text not null,
  scope text not null,
  related_task text,
  related_hypothesis text,
  related_commit text,
  supersedes text,
  status text not null default 'ACTIVE' check (status in ('ACTIVE','SUPERSEDED','RETIRED')),
  created_at timestamptz not null default now(),
  effective_at timestamptz not null default now(),
  recorded_by text not null
);
create unique index if not exists owner_decisions_active_title_idx on public.owner_decisions(title) where status='ACTIVE';
alter table public.owner_decisions enable row level security;
drop policy if exists owner_decisions_public_read on public.owner_decisions;
create policy owner_decisions_public_read on public.owner_decisions for select to anon, authenticated using (true);

create table if not exists public.agent_recommendations (
  id bigint generated always as identity primary key,
  agent text not null,
  recommendation text not null,
  reasoning text not null,
  scope text not null,
  related_task text,
  related_decision bigint references public.owner_decisions(id),
  owner_disposition text not null default 'PROPOSED' check (owner_disposition in ('PROPOSED','APPROVED','REJECTED','SUPERSEDED')),
  owner_note text,
  implementation_status text not null default 'NOT_IMPLEMENTED' check (implementation_status in ('NOT_IMPLEMENTED','IMPLEMENTED','VERIFIED','ROLLED_BACK')),
  related_commit text,
  created_at timestamptz not null default now()
);
alter table public.agent_recommendations enable row level security;
drop policy if exists agent_recommendations_public_read on public.agent_recommendations;
create policy agent_recommendations_public_read on public.agent_recommendations for select to anon, authenticated using (true);

insert into public.owner_decisions (decision_type,title,decision,owner_reason,scope,related_task,status,recorded_by)
select 'PRODUCT_DIRECTION','Complete truthful owner observability','Preserve complete research evidence and prioritize readability with truthful observability.','The dashboard is a result and observability surface; completeness and research integrity take priority over artificial speed or simplification.','Dashboard presentation, loading state, provenance, and governance memory','dashboard-owner-grade-presentation-2026-09-10','ACTIVE','human owner'
where not exists (select 1 from public.owner_decisions where title='Complete truthful owner observability' and status='ACTIVE');

insert into public.agent_recommendations (agent,recommendation,reasoning,scope,related_task,related_decision,owner_disposition,owner_note,implementation_status)
select 'implementation agent','Improve confidence-interval presentation and add a clear initial loading state.','The owner should understand estimate, interval, zero boundary, and promotion decision without losing research detail.','Dashboard research presentation and initial loading behavior','dashboard-owner-grade-presentation-2026-09-10',(select id from public.owner_decisions where title='Complete truthful owner observability' and status='ACTIVE' limit 1),'APPROVED','Approved by the owner in the implementation brief.','IMPLEMENTED'
where not exists (select 1 from public.agent_recommendations where recommendation='Improve confidence-interval presentation and add a clear initial loading state.' and owner_disposition='APPROVED');
