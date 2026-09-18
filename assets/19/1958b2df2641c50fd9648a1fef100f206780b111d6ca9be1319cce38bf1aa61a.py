from pathlib import Path
import sys,csv,json
import cv2,numpy as np
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'experiments/s2_bounded_20260908'))
import s2_preview_core_center365 as m
records=[]
for run in ['20260908_122758_325453','20260908_123353_407068','20260908_123420_353201']:
 p=root/'experiment_data'/run
 logged={int(x['frame']):x for x in csv.DictReader((p/'frames.csv').open())}
 for path in sorted(p.glob('*_raw.png')):
  f=cv2.imread(str(path));r=m.analyze(f);n=int(path.name.split('_')[0]);top=int(f.shape[0]*.55)
  white,yellow=m._SCOPE['build_color_masks'](f[top:]);value=cv2.cvtColor(f[top:],cv2.COLOR_BGR2HSV)[:,:,2]
  row=dict(run=run,frame=n,status=r['control_status'],matches_log=r['control_status']==logged[n]['control_status'],points=r['points'],bands=[])
  for i,y in enumerate(r['ys']):
   row['bands'].append(dict(y=int(y),selected_white=r['chosen'].get(i),white_candidates=m._SCOPE['road_white_segments'](white,value,y-top),yellow_candidates=m._SCOPE['segments'](yellow,y-top)))
  records.append(row)
out=Path(__file__).with_name('audit.json');out.write_text(json.dumps(records,indent=2))
print('saved frames',len(records),'status mismatches',sum(not x['matches_log'] for x in records))
for x in records:
 if x['status']!='ready': print(x)
