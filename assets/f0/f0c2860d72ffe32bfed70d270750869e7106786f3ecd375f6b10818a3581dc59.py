"""Offline-only edge audit. No hardware imports or driving entry point."""
import cv2
import numpy as np
import s2_preview_core_context as base
original_analyze = base.analyze
raw_white = None

def road_white_segments(mask, value, y):
    xs=np.flatnonzero(mask[y]>0)
    if not len(xs): return []
    result=[]
    for g in np.split(xs,np.where(np.diff(xs)>1)[0]+1):
        if not 2<=len(g)<=mask.shape[1]*.18:continue
        left=int(g[0]);edge=left;bridged=False
        while edge>0 and left-edge<6:
            if raw_white[y,edge-1]:edge-=1
            elif (not bridged and edge>=3 and left-edge<=3 and
                  raw_white[y,edge-2] and raw_white[y,edge-3]):
                edge-=3;bridged=True
            else:break
        flank=value[y,max(0,edge-7):max(0,edge-1)]
        if len(flank)<4 or np.mean(flank<145)<.8:continue
        result.append(float(g.mean()))
    return result

def analyze(frame):
    global raw_white
    top=int(frame.shape[0]*.55)
    hsv=cv2.cvtColor(frame[top:],cv2.COLOR_BGR2HSV)
    raw_white=cv2.inRange(hsv,np.array([0,0,145]),np.array([179,80,255]))
    original=base._SCOPE['road_white_segments']
    base._SCOPE['road_white_segments']=road_white_segments
    try:return original_analyze(frame)
    finally:base._SCOPE['road_white_segments']=original
