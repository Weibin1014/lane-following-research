from pathlib import Path
import sys,csv,json,importlib,time
import numpy as np
import cv2
p=Path('experiment_data/20260908_141942_363205');out=Path('experiments/s2_curve_audit_20260908/continuous_comparison');out.mkdir(exist_ok=True)
rows=list(csv.DictReader((p/'frames.csv').open()));images=sorted(p.glob('*_raw.png'));assert len(images)==len(rows)==320
frames=[cv2.imread(str(x)) for x in images]
versions=['thin','window','paths','width','independent'];report={}
for name in versions:
 m=importlib.import_module('s2_preview_core_'+name);results=[];bad=[];start=None;steps=[];last=None
 for i,f in enumerate(frames):
  t=time.perf_counter();a=m.analyze(f);ms=(time.perf_counter()-t)*1000
  ok=a['control_status']=='ready'
  results.append(dict(frame=i+1,elapsed_s=rows[i]['elapsed_s'],ready=ok,source=a.get('target_source','paired' if ok else 'unavailable'),pwm=a['steering_pwm'],near=a.get('near_x'),far=a.get('far_x'),reason=a.get('pair_status'),ms=ms))
  if not ok and start is None:start=i
  if start is not None and (ok or i==len(frames)-1):
   end=i-1 if ok else i;bad.append(dict(first=start+1,last=end+1,frames=end-start+1,span_s=float(rows[end]['elapsed_s'])-float(rows[start]['elapsed_s'])));start=None
  if ok and last is not None:steps.append((abs(a['steering_pwm']-last),i+1))
  last=a['steering_pwm'] if ok else None
 with (out/(name+'.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
 valid=[r['pwm'] for r in results if r['ready']]
 report[name]=dict(ready=sum(r['ready'] for r in results),total=len(results),estimated=sum('estimated' in r['source'] for r in results),bad_intervals=bad,pwm_range=[min(valid),max(valid)],largest_steps=sorted(steps,reverse=True)[:5])
 print(name,json.dumps(report[name]))
(out/'summary.json').write_text(json.dumps(report,indent=2))
print('timestamps increasing',all(int(b['sensor_timestamp'])>int(a['sensor_timestamp']) for a,b in zip(rows,rows[1:])))
