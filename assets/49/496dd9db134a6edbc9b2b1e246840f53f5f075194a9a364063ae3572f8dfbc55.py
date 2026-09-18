"""Offline full-sequence replay only. No camera or PWM."""
from pathlib import Path
import argparse,csv,json,time,statistics
import cv2
from temporal_probe import Tracker
parser=argparse.ArgumentParser()
parser.add_argument('sequence', nargs='?', default='problem_sequence_results/20260908_141942_363205')
args=parser.parse_args()
p=Path(args.sequence)
rows=list(csv.DictReader((p/'frames.csv').open()));tracker=Tracker();results=[]
for row in rows:
    n=int(row['frame']);f=cv2.imread(str(p/f'{n:06d}_raw.png'))
    if f is None:raise RuntimeError('Missing frame '+str(n))
    before=time.perf_counter();r=tracker.analyze(f,int(row['sensor_timestamp'])/1e9)
    results.append(dict(frame=n,status=r['control_status'],source=r.get('target_source','paired' if r['control_status']=='ready' else 'unavailable'),pwm=r['steering_pwm'],ms=(time.perf_counter()-before)*1000))
out=Path('temporal_replay_results')/time.strftime('%Y%m%d_%H%M%S');out.mkdir(parents=True,exist_ok=False)
with (out/'frames.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
s=dict(frames=len(results),ready=sum(r['status']=='ready' for r in results),temporal_frames=[r['frame'] for r in results if r['source']=='temporal_estimated'],median_ms=statistics.median(r['ms'] for r in results),max_ms=max(r['ms'] for r in results))
(out/'summary.json').write_text(json.dumps(s,indent=2));print(json.dumps(s));print('结果目录:',out.resolve())
