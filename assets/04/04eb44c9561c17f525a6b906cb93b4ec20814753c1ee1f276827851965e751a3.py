from pathlib import Path
import ast,textwrap
BASE=Path(__file__).resolve().parent
old=BASE.parent/'s2_lookahead_20260907'
# Reuse only verified definitions; do not import or execute hardware scripts.
source=(old/'s2_preview_core.py').read_text()
tree=ast.parse(source)
# Obtain embedded sources from module syntax, avoiding evaluation of old top-level code.
loop=next(n for n in tree.body if isinstance(n,ast.For))
items=ast.literal_eval(loop.iter)
mask,v4=items[0][0],items[1][0]
start='        h, w = frame.shape[:2]';end='        totals[status] += 1'
block=textwrap.dedent(start+v4.split(start,1)[1].split(end,1)[0])
block=block.replace('candidates = [white_segments(white, y-top) for y in ys]',
'''value = cv2.cvtColor(frame[top:], cv2.COLOR_BGR2HSV)[:, :, 2]
candidates = [road_white_segments(white, value, y-top) for y in ys]''')
function='def detect(frame):\n'+textwrap.indent(block,'    ')+'\n    return status, chosen, ys, yellow\n'
header='''"""Experimental v2 boundary checks; static servo validation only."""
import ast
import cv2
import numpy as np
'''
loader=f'''
_SCOPE = {{'cv2':cv2, 'np':np}}
for source, names in [({mask!r}, {{'build_color_masks'}}), ({v4!r}, {{'segments','white_segments'}})]:
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {{n.name for n in nodes}}==names
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<functions>','exec'),_SCOPE)
'''
body='''
def road_white_segments(mask,value,y):
    xs=np.flatnonzero(mask[y]>0)
    if not len(xs):return []
    groups=np.split(xs,np.where(np.diff(xs)>1)[0]+1)
    result=[]
    for g in groups:
        if not 2<=len(g)<=mask.shape[1]*.18:continue
        left=int(g[0]); flank=value[y,max(0,left-7):max(0,left-1)]
        if len(flank)<4 or np.mean(flank<145)<.8:continue
        result.append(float(g.mean()))
    return result

_SCOPE['road_white_segments']=road_white_segments
_SCOPE['ratios']=np.arange(.90,.549,-.05)
_SCOPE['scope']=_SCOPE
'''
body+=f"exec(compile({function!r},'<detector>','exec'),_SCOPE)\n"
control=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='control'))
target=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='target'))
pairing='''
def consistent_pairs(frame,chosen,ys,yellow):
    h,w=frame.shape[:2];top=int(h*.55)
    value=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,2]
    nodes=[]
    rejected=[]
    for i,wx in chosen.items():
        y=ys[i]
        for yx in _SCOPE['segments'](yellow,y-top):
            if not .15*w<=wx-yx<=.85*w:continue
            lo=int(np.ceil(yx))+3;hi=int(np.floor(wx))-3
            strip=value[y,lo:hi]
            if len(strip)<8 or np.mean(strip<145)<.90:
                rejected.append((y/h,(wx+yx)/2,'bright_interior'))
                continue
            nodes.append((i,yx,wx,float(np.mean(strip<145))))
    nodes.sort()
    paths=[]
    for j,node in enumerate(nodes):
        i,yx,wx,quality=node
        options=[(1.+.1*quality,[j])]
        for score,path in paths:
            pi,pyx,pwx,pquality=nodes[path[-1]];gap=i-pi
            if not 1<=gap<=3:continue
            # Near->far: both boundaries continuous, lane width should shrink.
            if abs(yx-pyx)>.14*w*gap or abs(wx-pwx)>.14*w*gap:continue
            if (wx-yx)-(pwx-pyx)>.025*w*gap:continue
            score=score+1.+.1*quality-.10*(gap-1)
            options.append((score,path+[j]))
        # Bounded multi-history search, not a single collapsed path per candidate.
        paths.extend(sorted(options,key=lambda x:x[0],reverse=True)[:4])
    viable=[p for p in paths if len(p[1])>=3 and nodes[p[1][-1]][0]-nodes[p[1][0]][0]>=3]
    if not viable:return [],'insufficient_pairs',rejected
    viable.sort(key=lambda x:x[0],reverse=True);score,path=viable[0]
    selected={nodes[j][0]:(nodes[j][1]+nodes[j][2])/2 for j in path}
    for other_score,other_path in viable[1:]:
        if score-other_score>.5:break
        other={nodes[j][0]:(nodes[j][1]+nodes[j][2])/2 for j in other_path}
        shared=selected.keys() & other.keys()
        if len(shared)>=2 and np.median([abs(selected[i]-other[i]) for i in shared])>.08*w:
            return [],'ambiguous_pairs',rejected
    return sorted((ys[i]/h,x) for i,x in selected.items()),'consistent',rejected

def analyze(frame):
    status,chosen,ys,yellow=_SCOPE['detect'](frame)
    points,pair_status,rejected=consistent_pairs(frame,chosen,ys,yellow)
    result=control(points,frame.shape[1],status)
    result.update(track_status=status,points=points,chosen=chosen,ys=ys,
                  pair_status=pair_status,rejected=rejected)
    return result
'''
(BASE/'s2_preview_core_v2.py').write_text(header+loader+body+'\n'+target+'\n'+control+'\n'+pairing)
