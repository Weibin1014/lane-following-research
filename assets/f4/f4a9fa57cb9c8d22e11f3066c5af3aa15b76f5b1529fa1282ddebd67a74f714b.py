from pathlib import Path
import textwrap
BASE=Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07/20260907_153630')
ROOT=Path(__file__).resolve().parent
v4=(BASE/'v4_snapshot.py').read_text();mask=(BASE/'mask_snapshot.py').read_text()
start='        h, w = frame.shape[:2]';end='        totals[status] += 1'
block=textwrap.dedent(start+v4.split(start,1)[1].split(end,1)[0])
function='def detect(frame):\n'+textwrap.indent(block,'    ')+'\n    return status, chosen, ys, yellow\n'
header='''"""Experimental image-space preview controller; no actuator initialization here.
Keep original v4 ROI and masks. This is a steering hypothesis, not curvature estimation.
"""
import ast
import cv2
import numpy as np
'''
loader=f'''
_SCOPE = {{"cv2": cv2, "np": np}}
for source, names in [({mask!r}, {{"build_color_masks"}}), ({v4!r}, {{"segments", "white_segments"}})]:
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {{n.name for n in nodes}} == names
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<v4-functions>', 'exec'), _SCOPE)
_SCOPE['ratios'] = np.arange(.90, .549, -.05)
_SCOPE['scope'] = _SCOPE
exec(compile({function!r}, '<v4-detector>', 'exec'), _SCOPE)
'''
body='''
def target(points, y):
    for py, x in points:
        if abs(py-y) < 1e-6:
            return x, 'direct'
    above = [p for p in points if p[0] < y]
    below = [p for p in points if p[0] > y]
    if above and below:
        y0, x0 = above[-1]; y1, x1 = below[0]
        if y1-y0 <= .15+1e-6:
            return x0+(y-y0)/(y1-y0)*(x1-x0), 'interpolated'
    return None, 'unavailable'

def control(points, width, track_status='selected'):
    near, near_status = target(points, .65)
    result = dict(near_x=near, near_status=near_status, far_x=None, far_y=None,
                  far_status='unavailable', near_offset=None, preview_error=None,
                  steering_pwm=350, control_status='unavailable')
    if track_status != 'selected' or near is None:
        return result
    near_offset = (near-width/2)/(width/2)
    result['near_offset'] = near_offset
    # Always require the original near target. Never replace it with a far-only target.
    for y in (.55, .60):
        far, far_status = target(points, y)
        if far is not None:
            break
    if far is None:
        return result
    far_offset = (far-width/2)/(width/2)
    trend = (far_offset-near_offset) * (.10/(.65-y))
    # Heuristic image-space preview term, not a measured road curvature or target point.
    preview = float(np.clip(near_offset + 1.5*trend, -1, 1))
    command = int(round(350-(40 if preview < 0 else 20)*float(np.clip(preview/.5,-1,1))))
    result.update(far_x=far, far_y=y, far_status=far_status, preview_error=preview,
                  steering_pwm=command, control_status='ready')
    return result

def analyze(frame):
    status, chosen, ys, yellow = _SCOPE['detect'](frame)
    h, w = frame.shape[:2]; top = int(h*.55)
    points = []
    for i, wx in chosen.items():
        possible = [x for x in _SCOPE['segments'](yellow, ys[i]-top) if .15*w <= wx-x <= .85*w]
        if len(possible) == 1:
            points.append((ys[i]/h, (wx+possible[0])/2))
    points.sort()
    result = control(points, w, status)
    result.update(track_status=status, points=points, chosen=chosen, ys=ys)
    return result
'''
(ROOT/'s2_preview_core.py').write_text(header+loader+body)
