from pathlib import Path
import csv,json,collections
import cv2
import quadratic_candidate as candidate
import s2_preview_core_local as base
root=Path(__file__).resolve().parents[2]
rows=[]
for p in sorted((root/'experiment_data').rglob('*_raw.*')):
 if p.suffix.lower() not in ('.png','.jpg','.jpeg'):continue
 f=cv2.imread(str(p))
 if f is None or f.shape[:2]!=(120,160):continue
 a=base.analyze(f);b=candidate.analyze(f)
 rows.append(dict(path=str(p.relative_to(root)),old=a['control_status'],new=b['control_status'],old_pwm=a['steering_pwm'],new_pwm=b['steering_pwm']))
Path(__file__).with_name('quadratic_results.json').write_text(json.dumps(rows,indent=2))
print(len(rows),collections.Counter((x['old'],x['new']) for x in rows))
for x in rows:
 if x['old']!=x['new']:print(x)
print('floor',collections.Counter((x['old'],x['new']) for x in rows if '/20260907_134704/' in x['path']))
