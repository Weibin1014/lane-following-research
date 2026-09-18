"""Offline-only prototype. No hardware entry point."""
import numpy as np
import cv2
import s2_preview_core_paths as base

def analyze(frame):
    original=base.analyze(frame)
    original=dict(original)
    original['target_source']='paired' if original['control_status']=='ready' else 'unavailable'
    if original['control_status']=='ready':return original
    options=base._SCOPE.get('audit_options',[])
    if not options or len(options)>64:return original
    _,_,ys,yellow=base._SCOPE['detect'](frame)
    h,w=frame.shape[:2];top=max(0,int(h*.55)-6)
    value=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,2]
    valid=[]
    for _,track in options:
        anchors=[]
        for i,wx in track:
            candidates=[]
            for yx in base._SCOPE['segments'](yellow,ys[i]-top):
                if not .15*w<=wx-yx<=.85*w:continue
                strip=value[ys[i],int(np.ceil(yx))+3:int(np.floor(wx))-3]
                if len(strip)>=8 and np.mean(strip<145)>=.9:candidates.append(wx-yx)
            if len(candidates)==1:anchors.append((ys[i]/h,candidates[0]))
        if len(anchors)<4:continue
        yy=np.array([a[0] for a in anchors]);ww=np.array([a[1] for a in anchors])
        if np.ptp(yy)<.15:continue
        coef=np.polyfit(yy,ww,1)
        if coef[0]<=0 or max(abs(np.polyval(coef,yy)-ww))>.03*w:continue
        points=[]
        for i,wx in track:
            y=ys[i]/h
            # Interpolate only within observed paired support; do not extrapolate.
            if not yy.min()<=y<=yy.max():continue
            width=float(np.polyval(coef,y))
            if not .15*w<=width<=.85*w:continue
            left=wx-width
            if left<0:continue
            strip=value[ys[i],int(np.ceil(left))+3:int(np.floor(wx))-3]
            if len(strip)<8 or np.mean(strip<145)<.9:continue
            points.append((y,wx-width/2))
        points.sort()
        result=base.control(points,w,'selected')
        if result['control_status']=='ready':
            result['model_points']=points
            valid.append(result)
    if not valid:return original
    for x in valid[1:]:
        shared_far=max(x['far_y'],valid[0]['far_y'])
        ax,_=base.target(x['model_points'],shared_far)
        bx,_=base.target(valid[0]['model_points'],shared_far)
        if ax is None or bx is None or abs(x['near_x']-valid[0]['near_x'])>.04*w or abs(ax-bx)>.04*w:return original
    result=dict(original);result.update(valid[0]);result['pair_status']='experimental_width_model'
    result['target_source']='width_estimated'
    result['near_status']='estimated'
    result['far_status']='estimated'
    result['points']=result.pop('model_points')
    return result
