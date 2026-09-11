from pathlib import Path

api=Path(__file__).resolve().parents[1]/'src'/'btc_research'/'api.py'
s=api.read_text()
old="""    async def sw1_claude_scan(self,as_of_ms:int|None,fee_bps:float=4.0,slippage_bps:float=1.0,funding_lookback:int=3)->list[dict[str,Any]]:
        text_as_of=str(as_of_ms) if as_of_ms is not None else None
        return await self.db.rpc(\"research_sw1_scan_frozen\",{\"p_as_of_ms\":text_as_of,\"p_fee_bps\":fee_bps,\"p_slippage_bps\":slippage_bps,\"p_funding_lookback\":funding_lookback})
"""
new=old+"""    async def hmr1_readiness(self,as_of_ms:int,p_oos_start_ms:int|None=None)->list[dict[str,Any]]:
        return await self.db.rpc(\"research_hmr1_readiness\",{\"p_as_of_ms\":as_of_ms,\"p_oos_start_ms\":p_oos_start_ms})
"""
if old not in s: raise SystemExit('API insertion point not found')
s=s.replace(old,new,1)
marker='@app.get("/api/v1/research/sw1-manus")\n'
route="""@app.get(\"/api/v1/research/hmr1/readiness\")
async def research_hmr1_readiness(p_oos_start_ms:int|None=Query(None,ge=0))->dict[str,Any]:
    \"\"\"Readiness-only H-MR1 gate surface; never runs the outcome RPC.\"\"\"
    try:
        latest=await app.state.live.latest_ohlcv(1)
        if not latest:return {\"status\":\"NO_DATA\",\"data\":None,\"trading_enabled\":False,\"outcome_run\":False}
        as_of_ms=int(latest[0][\"open_time_ms\"])
        rows=await app.state.live.hmr1_readiness(as_of_ms,p_oos_start_ms)
        return {\"status\":\"READINESS_ONLY\",\"data\":rows[0] if rows else None,\"trading_enabled\":False,\"outcome_run\":False}
    except Exception as exc:raise HTTPException(status_code=503,detail=\"H-MR1 readiness unavailable\") from exc

"""
if marker not in s: raise SystemExit('route marker not found')
s=s.replace(marker,route+marker,1)
api.write_text(s)

dash=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s= dash.read_text()
old_panel='''</section><section class="panel"><h2>Data stores</h2><div class="row"><span>OHLCV</span><strong id="ohlcvState">—</strong></div><div class="row"><span>Funding</span><strong id="fundingState">—</strong></div><div class="row"><span>Audit events</span><strong id="terminalEvents">—</strong></div><div class="row"><span>Latest funding</span><strong id="terminalFunding">—</strong></div></section></div>'''
new_panel='''</section><section class="panel"><h2>Data stores</h2><div class="row"><span>OHLCV</span><strong id="ohlcvState">—</strong></div><div class="row"><span>Funding</span><strong id="fundingState">—</strong></div><div class="row"><span>Audit events</span><strong id="terminalEvents">—</strong></div><div class="row"><span>Latest funding</span><strong id="terminalFunding">—</strong></div></section></div>
<div class="section-label">H-MR1 readiness gate</div><section class="panel full"><div class="notice"><span class="notice-mark warn">●</span><div><strong id="hmr1ReadinessStatus" class="warn">NOT READY</strong><br><span class="meta">Readiness facts only. Outcome is not run and authorization is not granted.</span><div class="decision-grid"><div class="metric"><small>Coverage / continuity</small><b id="hmr1Coverage">UNAVAILABLE</b></div><div class="metric"><small>Exact predecessor</small><b id="hmr1Predecessor">UNAVAILABLE</b></div><div class="metric"><small>Entry / exit</small><b id="hmr1Fills">UNAVAILABLE</b></div><div class="metric"><small>Training / OOS</small><b id="hmr1Split">UNAVAILABLE</b></div><div class="metric"><small>Complete ISO weeks</small><b id="hmr1Weeks">UNAVAILABLE</b></div><div class="metric"><small>OOS boundary</small><b id="hmr1Boundary">UNAVAILABLE</b></div><div class="metric"><small>Outcome</small><b id="hmr1Outcome">UNRUN</b></div></div></div></div></section>'''
if old_panel not in s: raise SystemExit('dashboard data store panel not found')
s=s.replace(old_panel,new_panel,1)
old_load="""async function loadTerminal(){try{const [h,o,f,l,r]=await Promise.all([get('/health'),get('/api/v1/market/ohlcv/latest?limit=1'),get('/api/v1/funding/latest'),get('/api/v1/signals/log?limit=50'),get('/api/v1/research/hfb1')].map(p=>p.catch(()=>null)));"""
new_load="""async function loadTerminal(){try{const [h,o,f,l,r,readiness]=await Promise.all([get('/health'),get('/api/v1/market/ohlcv/latest?limit=1'),get('/api/v1/funding/latest'),get('/api/v1/signals/log?limit=50'),get('/api/v1/research/hfb1'),get('/api/v1/research/hmr1/readiness')].map(p=>p.catch(()=>null)));"""
if old_load not in s: raise SystemExit('loadTerminal signature not found')
s=s.replace(old_load,new_load,1)
old_render="""$('terminalFetched').textContent=now();renderResult('hfb',r);renderWhiskers()}catch(e){offline();['terminalHealth','terminalAge','terminalCollector','terminalMarket','terminalEvents','terminalFunding','terminalFetched','ohlcvState','fundingState','auditCount','lastEvent','hfbN','hfbNet','hfbCI','hfbWin'].forEach(id=>{if($(id))$(id).textContent='UNAVAILABLE'})}}"""
new_render="""$('terminalFetched').textContent=now();renderResult('hfb',r);renderWhiskers();const rd=readiness?.data;if(rd){$('hmr1ReadinessStatus').textContent=rd.status||'NOT READY';$('hmr1ReadinessStatus').className=rd.status==='DATA_READY_OOS_BOUNDARY_FROZEN'?'ok':'warn';$('hmr1Coverage').textContent=fmt(rd.candle_count,0)+' / '+fmt(rd.expected_minute_count,0)+' · '+(rd.continuity_ok?'CONTINUOUS':'GAPS');$('hmr1Predecessor').textContent=fmt(rd.exact_predecessor_count,0)+' · '+fmt(Number(rd.exact_predecessor_rate)*100,2)+'%';$('hmr1Fills').textContent=fmt(rd.entry_available_count,0)+' / '+fmt(rd.exit_available_count,0);$('hmr1Split').textContent=fmt(rd.training_candles,0)+' / '+fmt(rd.oos_candles,0);$('hmr1Weeks').textContent=fmt(rd.complete_iso_weeks,0);$('hmr1Boundary').textContent=rd.oos_boundary_frozen?'FROZEN':'NOT FROZEN';$('hmr1Outcome').textContent=rd.outcome_run?'RUN':'UNRUN'}else{['hmr1ReadinessStatus','hmr1Coverage','hmr1Predecessor','hmr1Fills','hmr1Split','hmr1Weeks','hmr1Boundary'].forEach(id=>$(id).textContent='UNAVAILABLE');$('hmr1Outcome').textContent='UNRUN'}}catch(e){offline();['terminalHealth','terminalAge','terminalCollector','terminalMarket','terminalEvents','terminalFunding','terminalFetched','ohlcvState','fundingState','auditCount','lastEvent','hfbN','hfbNet','hfbCI','hfbWin','hmr1ReadinessStatus','hmr1Coverage','hmr1Predecessor','hmr1Fills','hmr1Split','hmr1Weeks','hmr1Boundary'].forEach(id=>{if($(id))$(id).textContent='UNAVAILABLE'});$('hmr1Outcome').textContent='UNRUN'}}}"""
if old_render not in s: raise SystemExit('loadTerminal render tail not found')
s=s.replace(old_render,new_render,1)
dash.write_text(s)
print('H-MR1 readiness surface added')
