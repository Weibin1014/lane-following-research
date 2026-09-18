"""Offline independent-boundary prototype. Never controls hardware."""
import cv2
import numpy as np
import s2_preview_core_paths as base

def analyze(frame):
    original=base.analyze(frame)
    if original['control_status']=='ready':return original
    options=base._SCOPE.get('audit_options',[])
    if not options or len(options)>64:return original
    h,w=frame.shape[:2];top=max(0,int(h*.55)-6)
    _,yellow=base._SCOPE['build_color_masks'](frame[top:])
    value=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,2]
    anchors=[]
    # Connected yellow paint fragments, not unrelated per-row detections.
    count,labels,stats,centroids=cv2.connectedComponentsWithStats(yellow,8)
    accepted=[]
    for label in range(1,count):
        x,y,bw,bh,area=stats[label]
        if area<8 or bw>.25*w or centroids[label][0]>=.65*w:continue
        accepted.append(label)
    for row in range(int(h*.55),int(h*.9)+1):
        xs=np.flatnonzero(np.isin(labels[row-top],accepted))
        if len(xs)>=2:
            groups=np.split(xs,np.where(np.diff(xs)>1)[0]+1)
            groups=[g for g in groups if len(g)>=2]
            if len(groups)==1:anchors.append((row/h,float(groups[0].mean())))
    if len(anchors)<8:return original
    a=np.array(anchors);yy=a[:,0];xx=a[:,1]
    if np.ptp(yy)<.20:return original
    coef=np.polyfit(yy,xx,2)
    residual=abs(np.polyval(coef,yy)-xx)
    inliers=residual<=.025*w
    if np.mean(inliers)<.9 or np.count_nonzero(inliers)<8:return original
    if not np.all(inliers):
        coef=np.polyfit(yy[inliers],xx[inliers],2)
        if max(abs(np.polyval(coef,yy[inliers])-xx[inliers]))>.025*w:return original
        yy=yy[inliers];xx=xx[inliers]
        if np.ptp(yy)<.20:return original
    results=[]
    _,_,ys,_=base._SCOPE['detect'](frame)
    for _,track in options:
        wp=sorted((ys[i]/h,x) for i,x in track)
        miny=max(yy.min(),wp[0][0]);maxy=min(yy.max(),wp[-1][0])
        if miny>.60 or maxy<.65:continue
        points=[]
        for y,wx in wp:
            if not miny<=y<=maxy:continue
            yx=float(np.polyval(coef,y));width=wx-yx
            if not .15*w<=width<=.85*w:continue
            strip=value[round(y*h),max(0,int(np.ceil(yx))+3):int(np.floor(wx))-3]
            if len(strip)<8 or np.mean(strip<145)<.9:continue
            points.append((y,(wx+yx)/2))
        if len(points)<4:continue
        r=base.control(points,w,'selected')
        if r['control_status']=='ready':
            r['points']=points;results.append(r)
    if not results:return original
    first=results[0]
    for other in results[1:]:
        y=max(first['far_y'],other['far_y'])
        ax,_=base.target(first['points'],y);bx,_=base.target(other['points'],y)
        if ax is None or bx is None or abs(ax-bx)>.04*w or abs(first['near_x']-other['near_x'])>.04*w:return original
    result=dict(original);result.update(first);result['target_source']='independent_estimated'
    result['near_status']=result['far_status']='estimated'
    return result
