from pathlib import Path
import json,csv,math,hashlib
ROOT=Path(__file__).resolve().parents[2]
data=ROOT/'experiment_data/2026-09-12/pixel_evaluation_20260912'
out=ROOT/'reports/pixel_evaluation_2026-09-12'
trials=[('CNN_03','CNN_RUN_20260912_082503_192901',2,1),('CNN_01R1','CNN_RUN_20260912_083059_817688',3,1),('CNN_02R1','CNN_RUN_20260912_083630_427620',2,0),('OpenCV_02','opencv_runs/20260912_082301_535034',0,0),('OpenCV_03','opencv_runs/20260912_082750_454344',0,0),('OpenCV_01R1','opencv_runs/20260912_083241_823654',0,0)]
result=[];hashes={};samples=[]
for name,rel,touch,exc in trials:
 p=data/rel
 if name.startswith('CNN'):
  rows=[json.loads(s) for f in sorted(p.glob('*.catalog')) for s in f.read_text().splitlines() if s.strip()]
  images=[p/'images'/r['cam/image_array'] for r in rows]
  times=[r['_timestamp_ms']/1000 for r in rows]
  valid=all(all(isinstance(r.get(k),(int,float)) and math.isfinite(r[k]) for k in ['pilot/angle','pilot/throttle']) and r['user/mode']=='local_angle' and r['user/throttle']==.375 for r in rows)
  candidates=list(zip(times,images))
 else:
  rows=list(csv.DictReader((p/'frames.csv').open()))
  images=sorted(p.glob('*_raw.png'));times=[int(r['sensor_timestamp'])/1e9 for r in rows]
  valid=all(r['fresh']=='True' and r['control_status']=='ready' for r in rows)
  # Use only saved frames whose log records a forward request.
  by_id={int(r['frame']):r for r in rows}
  candidates=[(int(by_id[int(f.name.split('_')[0])]['sensor_timestamp'])/1e9,f) for f in images if float(by_id[int(f.name.split('_')[0])]['requested_throttle'])==400]
 assert rows and images and valid and all(f.is_file() for f in images)
 assert all(b>a for a,b in zip(times,times[1:]))
 d={'trial':name,'directory':str(p),'records':len(rows),'images':len(images),'record_span_s':round(times[-1]-times[0],3),'line_touches':touch,'out_of_bounds':exc,'interventions':0,'valid':valid}
 result.append(d)
 # Preselect evenly spaced times without scoring or selecting good-looking frames.
 for i in range(10):
  target=candidates[0][0]+(candidates[-1][0]-candidates[0][0])*i/9
  t,f=min(candidates,key=lambda pair:abs(pair[0]-target))
  samples.append({'trial':name,'sample':i+1,'image':str(f),'relative_time_s':round(t-candidates[0][0],3),'measurement_y':'','left_x':'','right_x':'','status':'pending','note':''})
 for f in sorted(p.rglob('*')):
  if f.is_file():hashes[str(f.relative_to(data))]=hashlib.sha256(f.read_bytes()).hexdigest()
(out/'six_run_audit.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
with (out/'annotation_samples.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(samples[0]));w.writeheader();w.writerows(samples)
for d in result:print(d)
print('Candidate sample count:',len(samples),'Hashed files:',len(hashes))
print('All CNN run counts (including unclassified):')
for p in sorted(data.glob('CNN_RUN_*')):print(p.name,len(list(p.rglob('*.jpg'))))
