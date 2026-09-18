import csv,cv2,json,importlib
from pathlib import Path
out={}
for version in ['independent','midfar','nearfar']:
 m=importlib.import_module('s2_preview_core_'+version);out[version]={}
 for run in ['20260908_141942_363205','20260908_142524_316400']:
  p=Path('experiment_data')/run;rr=[]
  for row in csv.DictReader((p/'frames.csv').open()):
   n=int(row['frame']);r=m.analyze(cv2.imread(str(p/f'{n:06d}_raw.png')))
   rr.append(dict(frame=n,ready=r['control_status']=='ready',pwm=r['steering_pwm'],far_y=r.get('far_y')))
  jumps=[abs(b['pwm']-a['pwm']) for a,b in zip(rr,rr[1:]) if a['ready'] and b['ready']]
  print(version,run,'ready',sum(r['ready'] for r in rr),'maxstep',max(jumps),'short baseline',sum(r['far_y']==.625 for r in rr))
  out[version][run]=rr
Path('experiments/s2_curve_audit_20260908/far_options_results.json').write_text(json.dumps(out,indent=2))
