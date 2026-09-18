import ast,csv,textwrap,json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parent
BASE=Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07/20260907_153630')
def detector(roi):
    v4=(BASE/'v4_snapshot.py').read_text()
    mask=(BASE/'mask_snapshot.py').read_text()
    scope={'cv2':cv2,'np':np}
    for src,names in [(mask,{'build_color_masks'}),(v4,{'segments','white_segments'})]:
        nodes=[n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in names]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<functions>','exec'),scope)
    start='        h, w = frame.shape[:2]';end='        totals[status] += 1'
    block=textwrap.dedent(start+v4.split(start,1)[1].split(end,1)[0])
    block=block.replace('top = int(h * 0.55)',f'top = int(h * {roi})')
    scope['ratios']=np.arange(.90,roi-.001,-.05);scope['scope']=scope
    exec('def detect(frame):\n'+textwrap.indent(block,'    ')+'\n    return status, chosen, ys, yellow\n',scope)
    def run(frame):
        status,chosen,ys,yellow=scope['detect'](frame);h,w=frame.shape[:2];top=int(h*roi)
        points=[]
        for i,wx in chosen.items():
            possible=[x for x in scope['segments'](yellow,ys[i]-top) if .15*w<=wx-x<=.85*w]
            if len(possible)==1:points.append((ys[i]/h,(wx+possible[0])/2))
        return status,sorted(points),chosen,ys
    return run

def target(points,y):
    for py,x in points:
        if abs(py-y)<1e-6:return x,'direct'
    above=[p for p in points if p[0]<y];below=[p for p in points if p[0]>y]
    if above and below:
        y0,x0=above[-1];y1,x1=below[0]
        if y1-y0<=.15+1e-6:return x0+(y-y0)/(y1-y0)*(x1-x0),'interpolated'
    return None,'unavailable'
if __name__=='__main__':
    rows=[]
    runs=['133417','133705','133915','134112','134442','134704','150026','152620','153324','153630']
    engines={roi:detector(roi) for roi in [.55,.4]}
    for run in runs:
        for path in sorted(Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07',f'20260907_{run}').glob('*_raw.jpg')):
            frame=cv2.imread(str(path));w=frame.shape[1]
            for roi,engine in engines.items():
                status,points,chosen,ys=engine(frame)
                row=dict(run=run,image=path.name,roi=roi,status=status,points=json.dumps(points))
                for y in [.65,.6,.55,.5,.45]:
                    x,kind=target(points,y);row[f'offset{y}']='' if x is None else (x-w/2)/(w/2);row[f'status{y}']=kind
                rows.append(row)
    with (ROOT/'comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    for run in runs:
        for roi in engines:
            rr=[r for r in rows if r['run']==run and r['roi']==roi]
            summary={}
            for y in [.65,.6,.55,.5,.45]:
                a=[float(r[f'offset{y}']) for r in rr if r[f'offset{y}']!='']
                summary[y]=[len(a),round(float(np.median(a)),3) if a else None]
            print(run,roi,len(rr),summary)
