from pathlib import Path

api=Path(__file__).resolve().parents[1]/'src/btc_research/api.py'
s=api.read_text()
needle='''    async def hmr1_scan(self,oos_start_ms:int,as_of_ms:int,fee_bps:float=4.0,slippage_bps:float=1.0,stress_round_trip_bps:float=12.0)->list[dict[str,Any]]:
        return await self.db.rpc("research_hmr1_scan_frozen",{"p_oos_start_ms":oos_start_ms,"p_as_of_ms":as_of_ms,"p_fee_bps":fee_bps,"p_slippage_bps":slippage_bps,"p_stress_round_trip_bps":stress_round_trip_bps})
'''
replacement=needle+'''    async def hmr1_readiness(self,as_of_ms:int,p_oos_start_ms:int|None=None)->list[dict[str,Any]]:
        return await self.db.rpc("research_hmr1_readiness",{"p_as_of_ms":as_of_ms,"p_oos_start_ms":p_oos_start_ms})
'''
if needle not in s: raise SystemExit('hmr1 scan method not found')
s=s.replace(needle,replacement,1)
marker='@app.get("/api/v1/research/hmr1")\n'
route='''@app.get("/api/v1/research/hmr1/readiness")
async def research_hmr1_readiness(p_oos_start_ms:int|None=Query(None,ge=0))->dict[str,Any]:
    """Readiness-only H-MR1 surface; this route never runs the outcome scan."""
    try:
        latest=await app.state.live.latest_ohlcv(1)
        if not latest:return {"status":"NO_DATA","data":None,"trading_enabled":False,"outcome_run":False}
        as_of_ms=int(latest[0]["open_time_ms"])
        rows=await app.state.live.hmr1_readiness(as_of_ms,p_oos_start_ms)
        return {"status":"READINESS_ONLY","data":rows[0] if rows else None,"trading_enabled":False,"outcome_run":False}
    except Exception as exc:raise HTTPException(status_code=503,detail="H-MR1 readiness unavailable") from exc
'''
if marker not in s: raise SystemExit('hmr1 route marker not found')
s=s.replace(marker,route+marker,1)
api.write_text(s)

dash=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=dash.read_text()
needle='''<div class="research-explain"><strong>Research boundary:</strong> H-MR1 is registered and implemented as a read-only research path. The dashboard deliberately does not execute the OOS scan because the frozen OOS cutoff must be recorded before the first outcome is observed.</div></article></div>'''
addition='''<div class="research-explain"><strong>Research boundary:</strong> H-MR1 is registered and implemented as a read-only research path. The dashboard deliberately does not execute the OOS scan because the frozen OOS cutoff must be recorded before the first outcome is observed.</div><div class="metrics" style="margin-top:16px"><div class="metric wide"><small>Readiness state</small><b id="hmr1ReadinessStatus">UNAVAILABLE</b></div><div class="metric"><small>Coverage / continuity</small><b id="hmr1Coverage">UNAVAILABLE</b></div><div class="metric"><small>Exact predecessor</small><b id="hmr1Predecessor">UNAVAILABLE</b></div><div class="metric"><small>Entry / exit</small><b id="hmr1Fills">UNAVAILABLE</b></div><div class="metric"><small>Training / OOS</small><b id="hmr1Split">UNAVAILABLE</b></div><div class="metric"><small>Complete ISO weeks</small><b id="hmr1Weeks">UNAVAILABLE</b></div><div class="metric"><small>OOS boundary</small><b id="hmr1Boundary">NOT FROZEN</b></div><div class="metric"><small>Outcome</small><b id="hmr1Outcome">UNRUN</b></div></div></article></div>'''
if needle not in s: raise SystemExit('remote HMR1 card not found')
s=s.replace(needle,addition,1)
old='''async function loadResearch(){const [a,h3,b,c]=await Promise.all([safe('/api/v1/research/hfb1'),safe('/api/v1/research/hfb3'),safe('/api/v1/research/sw1-claude'),safe('/api/v1/research/sw1-manus')]);data={hfb:a,hfb3:h3,ref:b,ind:c};'''
new='''async function loadResearch(){const [a,h3,b,c,readiness]=await Promise.all([safe('/api/v1/research/hfb1'),safe('/api/v1/research/hfb3'),safe('/api/v1/research/sw1-claude'),safe('/api/v1/research/sw1-manus'),safe('/api/v1/research/hmr1/readiness')]);data={hfb:a,hfb3:h3,ref:b,ind:c};const rd=readiness?.data;if(rd){set('hmr1ReadinessStatus',rd.status||'NOT READY');set('hmr1Coverage',fmt(rd.candle_count,0)+' / '+fmt(rd.expected_minute_count,0)+' · '+(rd.continuity_ok?'CONTINUOUS':'GAPS'));set('hmr1Predecessor',fmt(rd.exact_predecessor_count,0)+' · '+fmt(Number(rd.exact_predecessor_rate)*100,2)+'%');set('hmr1Fills',fmt(rd.entry_available_count,0)+' / '+fmt(rd.exit_available_count,0));set('hmr1Split',fmt(rd.training_candles,0)+' / '+fmt(rd.oos_candles,0));set('hmr1Weeks',fmt(rd.complete_iso_weeks,0));set('hmr1Boundary',rd.oos_boundary_frozen?'FROZEN':'NOT FROZEN');set('hmr1Outcome',rd.outcome_run?'RUN':'UNRUN')}else{['hmr1ReadinessStatus','hmr1Coverage','hmr1Predecessor','hmr1Fills','hmr1Split','hmr1Weeks'].forEach(id=>set(id,'UNAVAILABLE'));set('hmr1Boundary','NOT FROZEN');set('hmr1Outcome','UNRUN')}'''
if old not in s: raise SystemExit('loadResearch remote signature not found')
s=s.replace(old,new,1)
dash.write_text(s)
print('remote H-MR1 readiness merged')
