"""Offline uncertainty-bounded local center fit; experimental, not a driver."""
import numpy as np
import cv2
import s2_preview_core_independent as base

def analyze(frame):
    original=base.analyze(frame)
    if original['control_status']=='ready':return original
    options=base._SCOPE.get('audit_options',[])
    if not options or len(options)>64:return original
    h,w=frame.shape[:2];top=max(0,int(h*.55)-6)
    _,_,ys,yellow=base._SCOPE['detect'](frame)
    value=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,2];valid=[]
    for _,track in options:
        points=[]
        for i,wx in track:
            y=ys[i]/h
            if not .55<=y<=.85:continue
            good=[]
            for yx in base._SCOPE['segments'](yellow,ys[i]-top):
                if not .15*w<=wx-yx<=.85*w:continue
                strip=value[ys[i],int(np.ceil(yx))+3:int(np.floor(wx))-3]
                if len(strip)>=8 and np.mean(strip<145)>=.9:good.append((wx+yx)/2)
            if len(good)==1:points.append((y,good[0]))
        if len(points)<3:continue
        a=np.array(points);yy=a[:,0];xx=a[:,1]
        span=np.ptp(yy)
        if span<.05-1e-6:continue
        extrap=max(yy.min()-.65,.65-yy.max(),0)
        if extrap>.05+1e-6:continue
        fit=np.polyfit(yy,xx,1);res=xx-np.polyval(fit,yy)
        if max(abs(res))>1.5:continue
        noise=max(.5,float(np.sqrt(np.sum(res**2)/max(1,len(xx)-2))))
        spread=np.sum((yy-yy.mean())**2)
        near_uncertainty=noise*np.sqrt(1/len(xx)+(.65-yy.mean())**2/spread)
        slope_uncertainty=noise/np.sqrt(spread)
        if near_uncertainty>1.5 or 150*1.5*.1*slope_uncertainty/(w/2)>8:continue
        near=float(np.polyval(fit,.65))
        offset=(near-w/2)/(w/2)
        preview=float(np.clip(offset-1.5*.1*fit[0]/(w/2),-1,1))
        # Do not introduce saturated steering from this new estimation branch.
        if abs(preview)>=.5:continue
        valid.append(dict(near_x=near,near_offset=offset,preview_error=preview,steering_pwm=int(round(365-75*float(np.clip(preview/.5,-1,1)))),model_points=sorted(points),near_extrapolation=extrap,near_uncertainty_px=near_uncertainty))
    if not valid:return original
    best=valid[0]
    if any(abs(x['near_x']-best['near_x'])>.04*w or abs(x['preview_error']-best['preview_error'])>.08 for x in valid[1:]):return original
    result=dict(original);result.update(best);result.update(control_status='ready',target_source='local_geometry_estimated',near_status='estimated',far_status='unavailable',far_x=None,far_y=None,pair_status='local_geometry_estimated',points=best['model_points'])
    return result
