from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dashboard/index.html"
html = path.read_text(encoding="utf-8")

old_data = '<div class="cell" style="margin-top:10px"><div class="k">Data integrity boundaries</div><div id="contaminationList" style="margin-top:8px">Reading contamination_intervals…</div></div>'
new_data = '''<div class="cell" style="margin-top:10px"><div class="k">Data integrity boundaries</div><div id="contaminationList" style="margin-top:8px">Reading contamination_intervals…</div></div>
<div style="height:10px"></div><div class="grid cols2"><div class="cell"><div class="k">Dataset registry</div><p style="margin-top:7px">Canonical metadata only. Raw historical payloads remain outside Supabase when practical.</p><div id="datasetRegistry" style="margin-top:8px">Reading research_dataset_registry…</div></div><div class="cell"><div class="k">Canonical hypothesis memory</div><p style="margin-top:7px">Persisted records from <span class="mono">research_hypothesis_records</span>; missing provenance stays explicit.</p><div id="canonicalHypotheses" style="margin-top:8px">Reading research_hypothesis_records…</div></div></div>'''
if old_data not in html:
    raise SystemExit("data anchor not found")
html = html.replace(old_data, new_data, 1)

old_sources = '<div class="source-item"><button data-doc="docs/RESEARCH_PROTOCOL.md">Research protocol</button><small>Git / main</small></div>'
new_sources = old_sources + '\n<div class="source-item"><button data-doc="docs/HISTORICAL_DATA_FINDINGS_QUEUE.md">Historical data findings queue</button><small>Git / main · findings only</small></div>\n<div class="source-item"><button data-doc="docs/HYPOTHESIS_RECORD_CONTRACT.md">Hypothesis record contract</button><small>Git / main · canonical</small></div>'
if old_sources not in html:
    raise SystemExit("source anchor not found")
html = html.replace(old_sources, new_sources, 1)

old_destructure = " const [hyp,results,lineage,contamination,health,decisions,gates,latest]=await Promise.all(["
new_destructure = " const [hyp,results,lineage,contamination,health,decisions,gates,latest,datasets,canonical]=await Promise.all(["
if old_destructure not in html:
    raise SystemExit("promise destructure target not found")
html = html.replace(old_destructure, new_destructure, 1)

old_fetch = "  safe('research_regression_gate?select=id,run_id,test_name,expected,observed,pass,evidence,created_at&order=created_at.desc&limit=12'),\n  safe('ohlcv_1m?select=open_time_ms,close&symbol=eq.BTCUSDT&interval=eq.1m&order=open_time_ms.desc&limit=1')"
new_fetch = "  safe('research_regression_gate?select=id,run_id,test_name,expected,observed,pass,evidence,created_at&order=created_at.desc&limit=12'),\n  safe('ohlcv_1m?select=open_time_ms,close&symbol=eq.BTCUSDT&interval=eq.1m&order=open_time_ms.desc&limit=1'),\n  safe('research_dataset_registry?select=dataset_id,source_type,source_uri,source_name,symbol,timeframe,storage_class,sha256,provenance_status,redistributable_status,immutable,created_at&order=created_at.desc&limit=50'),\n  safe('research_hypothesis_records?select=hypothesis_id,record_version,title,family,status,origin_type,origin_reference,research_question,provenance_status,source_documents,created_at&order=created_at.desc&limit=50')"
if old_fetch not in html:
    raise SystemExit("fetch anchor not found")
html = html.replace(old_fetch, new_fetch, 1)

old_assign = " const hs=remember('hyp',hyp),rs=remember('results',results),lm=remember('lineage',lineage),ci=remember('contamination',contamination),ch=remember('health',health),od=remember('decisions',decisions),gt=remember('gates',gates),lc=remember('latest',latest);"
new_assign = " const hs=remember('hyp',hyp),rs=remember('results',results),lm=remember('lineage',lineage),ci=remember('contamination',contamination),ch=remember('health',health),od=remember('decisions',decisions),gt=remember('gates',gates),lc=remember('latest',latest),ds=remember('datasets',datasets),cr=remember('canonical',canonical);"
if old_assign not in html:
    raise SystemExit("assign anchor not found")
html = html.replace(old_assign, new_assign, 1)

old_contam = " document.getElementById('contaminationList').innerHTML=Array.isArray(ci)&&ci.length?ci.map(x=>'<div style=\"padding:7px 0;border-top:1px solid var(--line)\"><b class=\"mono\">'+esc(iso(x.started_at))+' → '+esc(iso(x.ended_at))+'</b><br><span class=\"small\">'+esc(x.reason||'')+'</span></div>').join(''):'<span class=\"status ok\">NONE RECORDED</span>';"
new_contam = old_contam + "\n document.getElementById('datasetRegistry').innerHTML=Array.isArray(ds)&&ds.length?ds.map(x=>'<div style=\"padding:7px 0;border-top:1px solid var(--line)\"><b class=\"mono\">'+esc(x.dataset_id)+'</b> · '+esc(x.provenance_status||'UNSPECIFIED')+'<br><span class=\"small\">'+esc(x.source_name||x.source_uri||'—')+' · '+esc(x.symbol||'—')+' · '+esc(x.timeframe||'—')+' · immutable='+esc(x.immutable)+'</span></div>').join(''):'<span class=\"status warn\">NO EXTERNAL DATASETS REGISTERED · 0 ROWS</span>';\n document.getElementById('canonicalHypotheses').innerHTML=Array.isArray(cr)&&cr.length?cr.map(x=>'<div style=\"padding:7px 0;border-top:1px solid var(--line)\"><b class=\"mono\">'+esc(x.hypothesis_id)+' · v'+esc(x.record_version)+'</b> · '+esc(x.status||'UNSPECIFIED')+'<br><span class=\"small\">'+esc(x.title)+' · '+esc(x.origin_type)+' · '+esc(x.provenance_status||'UNSPECIFIED')+'<br>'+esc(x.origin_reference||'NOT_RECOVERABLE_FROM_CURRENT_RECORD')+'</span></div>').join(''):'<span class=\"status warn\">CANONICAL HYPOTHESIS MEMORY UNAVAILABLE</span>';"
if old_contam not in html:
    raise SystemExit("contamination anchor not found")
html = html.replace(old_contam, new_contam, 1)

old_agent = "const r=await safe('agent_coordination_log?select=task_id,status,owner,lane,updated_at,next_action,commit_sha,db_object&order=updated_at.desc&limit=40');"
new_agent = "const r=await safe('research_agent_activity_public?select=task_id,status,owner,lane,updated_at,next_action&order=updated_at.desc&limit=40');"
if old_agent not in html:
    raise SystemExit("agent target not found")
html = html.replace(old_agent, new_agent, 1)
html = html.replace("Anonymous dashboard read is not permitted for the coordination ledger.", "The public coordination summary is unavailable; no status is fabricated.", 1)

path.write_text(html, encoding="utf-8")
print("canonical archive bindings added")
