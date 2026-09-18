import ast
from pathlib import Path
import cv2
import numpy as np
from s2_preview_core_v2 import road_white_segments, consistent_pairs, control, analyze
# White candidate must have dark road immediately to its left.
m=np.zeros((1,160),np.uint8);m[0,70:75]=255
v=np.full((1,160),220,np.uint8)
assert road_white_segments(m,v,0)==[]
v[0,60:70]=60
assert road_white_segments(m,v,0)==[72.0]
# Pair path requires support across >=3 heights spanning >=15% image height.
frame=np.full((120,160,3),60,np.uint8);yellow=np.zeros((54,160),np.uint8)
for y in [108,96,84]:yellow[y-66-2:y-66+3,30:34]=255
points,status,_=consistent_pairs(frame,{0:120,2:110,4:100},[108,102,96,90,84],yellow)
assert status=='consistent' and len(points)==3
points,status,_=consistent_pairs(frame,{0:120,2:110},[108,102,96,90,84],yellow)
assert status=='insufficient_pairs'
# A bright corridor between markers must not qualify as dark track.
bright=np.full((120,160,3),220,np.uint8)
points,status,rejected=consistent_pairs(bright,{0:120,2:110,4:100},[108,102,96,90,84],yellow)
assert points==[] and len(rejected)==3
# Missing/ambiguous detection cannot issue steering away from center.
assert control([(.55,60),(.65,80)],160,'uncertain')['steering_pwm']==350
assert control([(.55,60)],160)['control_status']=='unavailable'
assert control([(.65,80)],160)['control_status']=='unavailable'
# Archived failure frame: far target should no longer jump into right background.
p=Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07/20260907_154634_461086/000395_raw.jpg')
r=analyze(cv2.imread(str(p)))
assert r['control_status']=='ready' and r['far_y']==.6 and r['far_x']<r['near_x'] and r['steering_pwm']>350
# Verify runner uses lossless images and only explicit servo-channel writes.
s=Path(__file__).with_name('realtime_preview_v2.py').read_text();compile(s,'runner','exec')
tree=ast.parse(s)
calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='set_pwm']
assert len(calls)==4 and all(n.args[0].value==1 for n in calls)
assert "_{suffix}.png" in s
print('PASS: road flank, pair support, bright corridor, missing targets, failure-frame direction, runner checks')
