import sys,csv
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'s2_lookahead_20260907'))
from s2_preview_core import analyze as old
from s2_preview_core_v2 import analyze as new
rows=[]
runs=['133417','133705','133915','134112','134442','134704','150026','152620','153324','153630','154634_461086']
for run in runs:
 for p in sorted(Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07',f'20260907_{run}').glob('*_raw.jpg')):
  im=cv2.imread(str(p));a=old(im);b=new(im)
  rows.append(dict(run=run,image=p.name,old_ready=a['control_status'],new_ready=b['control_status'],old_pwm=a['steering_pwm'],new_pwm=b['steering_pwm'],old_near=a['near_x'],new_near=b['near_x'],new_far=b['far_x'],pair_status=b['pair_status'],points=str(b['points'])))
  if run=='154634_461086' and p.name in ['000240_raw.jpg','000265_raw.jpg','000350_raw.jpg','000395_raw.jpg']:
   print(p.name,'OLD',a['control_status'],a['steering_pwm'],a['points'],'NEW',b['control_status'],b['steering_pwm'],b['points'])
   view=cv2.resize(im,(640,480));cv2.line(view,(320,0),(320,479),(255,255,0),1)
   for i,x in b['chosen'].items():cv2.circle(view,(round(x*4),b['ys'][i]*4),3,(255,255,0),-1)
   for y,x in b['points']:cv2.circle(view,(round(x*4),round(y*480)),4,(0,0,255),-1)
   for key,y,color in [('near_x',.65,(0,255,0)),('far_x',b['far_y'],(255,0,255))]:
    if b[key] is not None:cv2.circle(view,(round(b[key]*4),round(y*480)),9,color,2)
   cv2.putText(view,f"v2 {b['control_status']} PWM={b['steering_pwm']}",(8,22),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,255,0),1)
   cv2.imwrite(str(ROOT/p.name.replace('_raw','_v2')),view)
with (ROOT/'regression.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for run in runs:
 rr=[r for r in rows if r['run']==run];ready=[r for r in rr if r['new_ready']=='ready']
 print(run,len(rr),'old',sum(r['old_ready']=='ready' for r in rr),'new',len(ready),'pwm',np.median([r['new_pwm'] for r in ready]) if ready else None)
print('total',len(rows))
