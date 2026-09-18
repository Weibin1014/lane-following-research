from pathlib import Path
import csv,json
from collections import defaultdict
import cv2
import numpy as np
from s2_preview_core import analyze, control
ROOT=Path(__file__).resolve().parent
rows=[]
for run in ['133417','133705','133915','134112','134442','134704','150026','152620','153324','153630']:
 for p in sorted(Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07',f'20260907_{run}').glob('*_raw.jpg')):
  frame=cv2.imread(str(p));r=analyze(frame)
  rows.append(dict(run=run,image=p.name,**{k:v for k,v in r.items() if k not in ['points','chosen','ys']}))
  if p.name=='000001_raw.jpg' and run in ['133417','133705','133915','134112','134442','153630']:
   view=cv2.resize(frame,(640,480))
   cv2.line(view,(320,0),(320,479),(255,255,0),1)
   for y,x in r['points']:cv2.circle(view,(round(x*4),round(y*480)),4,(0,0,255),-1)
   if r['near_x'] is not None:cv2.circle(view,(round(r['near_x']*4),312),9,(0,255,0),2)
   if r['far_x'] is not None:cv2.circle(view,(round(r['far_x']*4),round(r['far_y']*480)),9,(255,0,255),2)
   cv2.putText(view,f"preview={r['preview_error']:.3f} pwm={r['steering_pwm']}",(8,22),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,255,0),1)
   cv2.imwrite(str(ROOT/f'preview_{run}.jpg'),view)
with (ROOT/'candidate_results.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for run in dict.fromkeys(r['run'] for r in rows):
 rr=[r for r in rows if r['run']==run];ready=[r for r in rr if r['control_status']=='ready']
 vals=lambda key:round(float(np.median([r[key] for r in ready])),4) if ready else None
 print(run,len(rr),'ready',len(ready),'near',vals('near_offset'),'preview',vals('preview_error'),'PWM',vals('steering_pwm'))
# Boundary behaviors independent of extraction.
assert control([],160)['steering_pwm']==350
assert control([(.55,60),(.60,65)],160)['control_status']=='unavailable'
assert control([(.65,80)],160)['control_status']=='unavailable'
assert control([(.55,60),(.65,80)],160,'uncertain')['control_status']=='unavailable'
assert control([(.55,60),(.65,80)],160)['steering_pwm']>350
assert control([(.55,100),(.65,80)],160)['steering_pwm']<350
assert all(330 <= r['steering_pwm'] <= 390 for r in rows)
print('PASS: missing targets, uncertain track, direction, PWM bounds.')
