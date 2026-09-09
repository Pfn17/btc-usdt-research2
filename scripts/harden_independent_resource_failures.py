from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dashboard'/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace("const [h,o,s,l,f]=await Promise.all([get('/health'),get('/api/v1/market/ohlcv/latest?limit=1'),get('/api/v1/signal/hfb1/current'),get('/api/v1/signals/log?limit=30'),get('/api/v1/funding/latest')]);const c=", "let [h,o,s,l,f]=await Promise.all([get('/health'),get('/api/v1/market/ohlcv/latest?limit=1'),get('/api/v1/signal/hfb1/current'),get('/api/v1/signals/log?limit=30'),get('/api/v1/funding/latest')].map(p=>p.catch(()=>null)));if(!h||!o)throw Error('overview core resource unavailable');s=s||{};l=l||{data:[]};f=f||{};const c=")
s=s.replace("const [h,o]=await Promise.all([get('/health'),get('/api/v1/market/ohlcv/latest?limit=24')]);setHeader(h);", "const [h,o]=await Promise.all([get('/health'),get('/api/v1/market/ohlcv/latest?limit=24')].map(p=>p.catch(()=>null)));if(!h||!o)throw Error('visual core resource unavailable');setHeader(h);")
s=s.replace("const [h,r,l,o]=await Promise.all([get('/health'),get('/api/v1/research/hfb1'),get('/api/v1/signals/log?limit=30'),get('/api/v1/market/ohlcv/latest?limit=1')]);const c=", "const [h,r,l,o]=await Promise.all([get('/health'),get('/api/v1/research/hfb1'),get('/api/v1/signals/log?limit=30'),get('/api/v1/market/ohlcv/latest?limit=1')].map(p=>p.catch(()=>null)));if(!h||!o)throw Error('story core resource unavailable');const c=")
s=s.replace("const c=(o.data||[])[0]||{},x=(r.data||[])[0]||{};setHeader(h);", "const c=(o.data||[])[0]||{},x=(r?.data||[])[0]||{};l=l||{data:[]};setHeader(h);")
s=s.replace("if(h.status==='ok'?'HEALTHY':'DEGRADED';", "if(h.status==='ok'?'HEALTHY':'DEGRADED';")
p.write_text(s,encoding='utf-8')
print('independent resource failure handling added')
