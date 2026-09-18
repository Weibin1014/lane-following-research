import csv,json,cv2
from pathlib import Path
import fragment_candidate as m
out={}
for run in ['20260908_141942_363205','20260908_142524_316400']:
 p=Path('experiment_data')/run;results=[]
 for row in csv.DictReader((p/'frames.csv').open()):
  n=int(row['frame']);r=m.analyze(cv2.imread(str(p/f'{n:06d}_raw.png')))
  results.append(dict(frame=n,status=r['control_status'],source=r.get('target_source','paired'),pwm=r['steering_pwm']))
 out[run]=results
 print(run,'ready',sum(x['status']=='ready' for x in results),'total',len(results),'failed',[x['frame'] for x in results if x['status']!='ready'])
Path('experiments/s2_curve_audit_20260908/fragment_results.json').write_text(json.dumps(out,indent=2))
