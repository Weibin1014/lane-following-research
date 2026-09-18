from pathlib import Path
import cv2
import white_width_candidate as m
root=Path(__file__).resolve().parents[2]
f=cv2.imread(str(root/'experiment_data/20260908_140048_382380/000076_raw.png'))
r=m.analyze(f)
assert r['target_source']=='width_estimated' and r['near_status']=='estimated' and r['far_status']=='estimated'
assert all(.55<=y<=.875 for y,x in r['points'])
original=m.base.analyze
segment=m.base._SCOPE['segments']
try:
 def initialized(frame):
  r=original(frame)
  m.base._SCOPE['audit_options']=[]
  return r
 m.base.analyze=initialized
 assert m.analyze(f)['control_status']=='unavailable'
 def overflow(frame):
  r=original(frame)
  m.base._SCOPE['audit_options']=[(0,[])]*65
  return r
 m.base.analyze=overflow
 assert m.analyze(f)['control_status']=='unavailable'
 m.base.analyze=original
 m.base._SCOPE['segments']=lambda *args:[]
 assert m.analyze(f)['control_status']=='unavailable'
finally:
 m.base.analyze=original;m.base._SCOPE['segments']=segment
print('PASS estimated provenance, observed-range output, no paths, candidate cap, no yellow support')
