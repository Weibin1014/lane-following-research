"""Image-file replay only: no camera or PWM dependencies."""
import argparse,csv,json,time,statistics,hashlib
from pathlib import Path
import cv2
from s2_preview_core_independent import analyze
RUNS=[('second_curve_thin_5s_results','20260908_133717_324605'),('second_curve_window_5s_results','20260908_134855_688477'),('second_curve_paths_5s_results','20260908_140048_382380'),('second_curve_width_5s_results','20260908_141033_123128')]
p=argparse.ArgumentParser();p.add_argument('--local-data',type=Path);args=p.parse_args()
rows=[];missing=[]
for folder,run in RUNS:
    directory=args.local_data/run if args.local_data else Path(folder)/run
    paths=sorted(directory.glob('*_raw.png'))
    if not paths:missing.append(str(directory));continue
    logged={int(r['frame']):r for r in csv.DictReader((directory/'frames.csv').open())}
    for path in paths:
        frame=cv2.imread(str(path))
        if frame is None:raise RuntimeError('Cannot read '+str(path))
        start=time.perf_counter();r=analyze(frame);ms=(time.perf_counter()-start)*1000
        n=int(path.name.split('_')[0])
        rows.append(dict(run=run,frame=n,logged_status=logged[n]['control_status'],status=r['control_status'],source=r.get('target_source','paired' if r['control_status']=='ready' else 'unavailable'),pwm=r['steering_pwm'],ms=ms))
if missing:raise RuntimeError('Missing directories: '+str(missing))
out=Path('independent_replay_results')/time.strftime('%Y%m%d_%H%M%S');out.mkdir(parents=True,exist_ok=False)
with (out/'frames.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(images=len(rows),ready=sum(x['status']=='ready' for x in rows),estimated=sum(x['source']=='independent_estimated' for x in rows),median_ms=statistics.median(x['ms'] for x in rows),max_ms=max(x['ms'] for x in rows),core_sha256=hashlib.sha256(Path(__file__).with_name('s2_preview_core_independent.py').read_bytes()).hexdigest())
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
for row in rows:
    if row['logged_status']!='ready':print('Recorded failure:',row)
print('Results:',out.resolve())
