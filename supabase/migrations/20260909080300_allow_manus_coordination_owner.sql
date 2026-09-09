-- Allow the Manus writer identity already documented in AGENTS.md to create auditable coordination entries.
ALTER TABLE public.agent_coordination_log
  DROP CONSTRAINT IF EXISTS agent_coordination_log_owner_check;

ALTER TABLE public.agent_coordination_log
  ADD CONSTRAINT agent_coordination_log_owner_check
  CHECK (owner = ANY (ARRAY['chatgpt'::text, 'claude-1'::text, 'claude-2'::text, 'claude-3'::text, 'human'::text, 'manus'::text]));

COMMENT ON CONSTRAINT agent_coordination_log_owner_check ON public.agent_coordination_log IS
  'Allowed project writers and auditors, including Manus as documented in AGENTS.md';
