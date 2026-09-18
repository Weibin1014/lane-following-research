from pathlib import Path
import sys,json
import cv2
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'experiments/s2_bounded_20260908'))
import s2_preview_core_center365 as m
original=m._SCOPE['build_color_masks']
rows=[]
for p in sorted((root/'experiment_data/2026-09-07').rglob('*_raw.*')):
 f=cv2.imread(str(p))
 if f is None:continue
 old=m.analyze(f);top=int(f.shape[0]*.55);start=max(0,top-3)
 def masks(roi):
  # Preserve yellow processing. Only give white opening real upper context.
  return original(f[start:])[0][top-start:],original(roi)[1]
 m._SCOPE['build_color_masks']=masks
 try:new=m.analyze(f)
 finally:m._SCOPE['build_color_masks']=original
 rows.append(dict(path=str(p.relative_to(root)),old=old['control_status'],new=new['control_status'],old_pwm=old['steering_pwm'],new_pwm=new['steering_pwm']))
Path(__file__).with_name('historical_check.json').write_text(json.dumps(rows,indent=2))
from collections import Counter
print('frames',len(rows));print(Counter((r['old'],r['new']) for r in rows))
print('changed commands',sum(r['old_pwm']!=r['new_pwm'] for r in rows))
