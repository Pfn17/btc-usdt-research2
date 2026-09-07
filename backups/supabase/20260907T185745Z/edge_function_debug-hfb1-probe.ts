import "jsr:@supabase/functions-js/edge-runtime.d.ts";

Deno.serve(async (_req: Request) => {
  const url = Deno.env.get("SUPABASE_URL");
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const attempts: Record<string, unknown> = {};

  const call = async (label: string, body: Record<string, unknown>) => {
    const res = await fetch(`${url}/rest/v1/rpc/research_funding_hfb1`, {
      method: "POST",
      headers: { apikey: key ?? "", Authorization: `Bearer ${key}`, "Content-Type": "application/json", Prefer: "return=representation" },
      body: JSON.stringify(body),
    });
    attempts[label] = { status: res.status, body: await res.text() };
  };

  await call("no_args", {});
  await call("explicit_nulls", { p_oos_start_ms: null, p_as_of_event_time_ms: null, p_fee_bps: null, p_slippage_bps: null });
  await call("numeric_args", { p_oos_start_ms: "1787040000000", p_as_of_event_time_ms: "1788600000000", p_fee_bps: 4, p_slippage_bps: 1 });
  return new Response(JSON.stringify(attempts, null, 2), { headers: { "Content-Type": "application/json" } });
});
