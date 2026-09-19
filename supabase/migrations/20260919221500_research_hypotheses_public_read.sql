-- Expose immutable hypothesis metadata to the owner-facing read-only dashboard.
-- No write, result, credential, or execution permission is granted here.
ALTER TABLE public.research_hypotheses ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS research_hypotheses_read_public ON public.research_hypotheses;
CREATE POLICY research_hypotheses_read_public
  ON public.research_hypotheses
  FOR SELECT
  TO anon, authenticated
  USING (true);

GRANT SELECT ON public.research_hypotheses TO anon, authenticated;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
  ON public.research_hypotheses FROM anon, authenticated;
