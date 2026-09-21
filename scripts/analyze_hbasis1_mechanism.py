import bisect, hashlib, json, math, os, random, statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

RAW=os.environ.get('HBASIS1_RAW','/tmp/hbasis1_raw.json')
OUT=os.environ.get('HBASIS1_OUT','/tmp/hbasis1_analysis.json')
rows=json.load(open(RAW))
rows.sort(key=lambda r:int(r['server_time_ms']))
times=[int(r['server_time_ms']) for r in rows]
basis=[float(r['basis_bps']) for r in rows]
# Frozen local baseline: prior elapsed 6h, minimum 30 observations.
window=6*60*60*1000
baselines=[]; residuals=[]
for i,t in enumerate(times):
    j=bisect.bisect_left(times,t-window,0,i)
    vals=basis[j:i]
    if len(vals)<30:
        baselines.append(None); residuals.append(None)
    else:
        b=statistics.median(vals); baselines.append(b); residuals.append(basis[i]-b)
train_end=1788825599999 # 2026-09-07T23:59:59.999Z
out_start=1788825600000 # 2026-09-08T00:00:00Z
abs_train=[abs(x) for t,x in zip(times,residuals) if x is not None and t<=train_end]
threshold=statistics.quantiles(abs_train,n=100,method='inclusive')[89]
# Describe autocorrelation on 1-step and elapsed-near-1m residuals, using valid pairs.
pairs=[]
for i in range(1,len(residuals)):
    if residuals[i] is not None and residuals[i-1] is not None and times[i]-times[i-1] <= 120000:
        pairs.append((residuals[i-1],residuals[i]))
def corr(ps):
    if len(ps)<2:return None
    a=[x for x,y in ps]; b=[y for x,y in ps]; ma=statistics.mean(a); mb=statistics.mean(b)
    da=sum((x-ma)**2 for x in a); db=sum((y-mb)**2 for y in b)
    return sum((x-ma)*(y-mb) for x,y in ps)/math.sqrt(da*db) if da and db else None
# Events per frozen horizon.
def first_at_or_after(target):
    return bisect.bisect_left(times,target)
def day(t): return datetime.fromtimestamp(t/1000,timezone.utc).date().isoformat()
def sign(x): return 1 if x>0 else -1 if x<0 else 0

def bootstrap_ci(values_by_day, seed=20260921, samples=2000):
    days=sorted(values_by_day)
    n=sum(len(values_by_day[d]) for d in days)
    if n==0:return {'mean':None,'ci_low':None,'ci_high':None,'n':0,'days':0}
    rng=random.Random(seed); means=[]
    for _ in range(samples):
        sample=[]
        while len(sample)<n:
            sample.extend(values_by_day[rng.choice(days)])
        means.append(statistics.mean(sample[:n]))
    means.sort()
    return {'mean':statistics.mean([v for d in days for v in values_by_day[d]]),'ci_low':means[int(.025*samples)],'ci_high':means[min(samples-1,int(.975*samples))],'n':n,'days':len(days)}

def bootstrap_ci_hours(events, field, block_hours, seed=20260921, samples=2000):
    blocks=defaultdict(list)
    block_ms=block_hours*60*60*1000
    for e in events:
        blocks[int(e['signal_ms'])//block_ms].append(e[field])
    return bootstrap_ci(blocks, seed=seed, samples=samples)

def summarize(events,h):
    out={}
    for split,es in [('train',[e for e in events if e['signal_ms']<=train_end]),('oos',[e for e in events if e['signal_ms']>=out_start])]:
        gross=[e['gross_bps'] for e in es]; net=[e['net_bps'] for e in es]; conv=[1 if e['converged_50'] else 0 for e in es if e['converged_50'] is not None]
        byday=defaultdict(list)
        cday=defaultdict(list)
        for e in es:
            byday[day(e['signal_ms'])].append(e['net_bps'])
            if e['converged_50'] is not None:cday[day(e['signal_ms'])].append(1 if e['converged_50'] else 0)
        ci=bootstrap_ci(byday)
        ci12=bootstrap_ci_hours(es,'net_bps',12)
        ci48=bootstrap_ci_hours(es,'net_bps',48)
        cci=bootstrap_ci(cday)
        times_to=[e['time_to_conv_min'] for e in es if e['time_to_conv_min'] is not None]
        out[split]={'n':len(es),'active_days':len(byday),'gross_mean_bps':statistics.mean(gross) if gross else None,'net_mean_bps':statistics.mean(net) if net else None,'stress_mean_bps':statistics.mean([x-2 for x in net]) if net else None,'hit_rate':sum(x>0 for x in net)/len(net) if net else None,'net_ci95_block_day':ci,'net_ci95_block_12h':ci12,'net_ci95_block_48h':ci48,'convergence_n':len(conv),'convergence_rate':statistics.mean(conv) if conv else None,'convergence_ci95_block_day':cci,'median_time_to_convergence_min':statistics.median(times_to) if times_to else None,'mean_time_to_convergence_min':statistics.mean(times_to) if times_to else None,'censored_exit_count':sum(1 for e in es if e['exit_ms'] is None),'mean_overshoot_ratio':statistics.mean([e['overshoot_ratio'] for e in es if e['overshoot_ratio'] is not None]) if es else None,'mean_adverse_excursion_bps':statistics.mean([e['adverse_excursion_bps'] for e in es if e['adverse_excursion_bps'] is not None]) if es else None,'net_by_day':{k:{'n':len(v),'mean_net_bps':statistics.mean(v)} for k,v in sorted(byday.items())}}
    return out

def build_events(horizon_min):
    candidates=[i for i,(t,r) in enumerate(zip(times,residuals)) if r is not None and abs(r)>=threshold]
    events=[]; last_scheduled_exit=-1
    for i in candidates:
        signal_ms=times[i]
        if signal_ms<=train_end and signal_ms < times[0]+window: continue
        if signal_ms < last_scheduled_exit: continue
        entry_i=first_at_or_after(signal_ms+60000)
        if entry_i>=len(rows): continue
        entry_ms=times[entry_i]
        exit_i=first_at_or_after(entry_ms+horizon_min*60000)
        if exit_i>=len(rows) or times[exit_i]>entry_ms+horizon_min*60000+120000:
            continue
        # Event is accepted only if exit baseline is available; otherwise censor it but retain event.
        entry_r=residuals[entry_i]; exit_r=residuals[exit_i]
        if entry_r is None or exit_r is None: continue
        scheduled_exit=entry_ms+horizon_min*60000
        last_scheduled_exit=scheduled_exit
        direction=-sign(entry_r)
        gross=(float(rows[exit_i]['mark_price'])/float(rows[entry_i]['mark_price'])-1)*10000*direction
        path=range(entry_i,exit_i+1)
        if direction==1:
            adverse=min((float(rows[k]['mark_price'])/float(rows[entry_i]['mark_price'])-1)*10000 for k in path)
        else:
            adverse=max((float(rows[k]['mark_price'])/float(rows[entry_i]['mark_price'])-1)*10000 for k in path)
        abs_entry=abs(entry_r); conv=abs(exit_r)<=.5*abs_entry
        tc=None
        for k in path:
            if abs(residuals[k])<=.5*abs_entry:
                tc=(times[k]-entry_ms)/60000; break
        overshoot=max(abs(residuals[k]) for k in path)/abs_entry if abs_entry else None
        events.append({'signal_ms':signal_ms,'entry_ms':entry_ms,'exit_ms':times[exit_i],'signal_residual_bps':residuals[i],'entry_residual_bps':entry_r,'exit_residual_bps':exit_r,'direction_proxy':'LONG' if direction==1 else 'SHORT','gross_bps':gross,'net_bps':gross-10,'converged_50':conv,'sign_crossed':sign(exit_r)!=sign(entry_r),'time_to_conv_min':tc,'overshoot_ratio':overshoot,'adverse_excursion_bps':adverse})
    return events

result={'freeze':{'train_end_ms':train_end,'oos_start_ms':out_start,'threshold_abs_residual_p90_train':threshold,'baseline_window_hours':6,'min_baseline_snapshots':30,'horizons_min':[5,15,30,60],'entry_delay_min':1,'exit_tolerance_min':2,'cost_baseline_rt_bps':10,'cost_stress_rt_bps':12,'block_bootstrap_seed':20260921,'block_bootstrap_samples':2000},'data':{'n':len(rows),'first_ms':times[0],'last_ms':times[-1],'interval_median_ms':statistics.median([times[i]-times[i-1] for i in range(1,len(times))]),'gaps_over_5m':sum(1 for i in range(1,len(times)) if times[i]-times[i-1]>300000),'max_gap_ms':max(times[i]-times[i-1] for i in range(1,len(times))),'basis_quantiles':{str(q):statistics.quantiles(basis,n=100,method='inclusive')[q-1] for q in [1,5,10,25,50,75,90,95,99]},'residual_autocorr_near_1m':corr(pairs),'residual_pair_count':len(pairs)},'horizons':{}}
for h in [5,15,30,60]:
    ev=build_events(h); result['horizons'][str(h)]={'events':len(ev),'summary':summarize(ev,h),'event_rows':ev}
with open(OUT,'w') as f: json.dump(result,f,indent=2)
print(json.dumps({k:v if k!='horizons' else {h:{'events':x['events'],'summary':x['summary']} for h,x in v.items()} for k,v in result.items()},indent=2))
