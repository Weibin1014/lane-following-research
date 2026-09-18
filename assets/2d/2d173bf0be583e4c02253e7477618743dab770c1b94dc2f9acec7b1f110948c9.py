"""Offline images only; no camera or PWM."""
from pathlib import Path
import csv,json,time,statistics
import cv2
from s2_preview_core_local import analyze
out=Path('local_geometry_replay_results')/time.strftime('%Y%m%d_%H%M%S');out.mkdir(parents=True)
for run in ['20260908_141942_363205','20260908_142524_316400']:
 p=Path('problem_sequence_results')/run;results=[]
 for row in csv.DictReader((p/'frames.csv').open()):
  n=int(row['frame']);f=cv2.imread(str(p/f'{n:06d}_raw.png'))
  if f is None:raise RuntimeError('Missing frame '+str(n))
  t=time.perf_counter();r=analyze(f)
  results.append(dict(frame=n,status=r['control_status'],source=r.get('target_source','paired'),pwm=r['steering_pwm'],ms=(time.perf_counter()-t)*1000))
 with (out/(run+'.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
 print(json.dumps(dict(run=run,frames=len(results),ready=sum(x['status']=='ready' for x in results),local_estimated=sum(x['source']=='local_geometry_estimated' for x in results),median_ms=statistics.median(x['ms'] for x in results),max_ms=max(x['ms'] for x in results))))
print('结果目录:',out.resolve())
