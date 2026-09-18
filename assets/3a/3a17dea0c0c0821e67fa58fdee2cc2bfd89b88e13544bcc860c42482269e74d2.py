"""Offline short-lived center/white relation propagation experiment."""
import numpy as np
import s2_preview_core_independent as base
class Tracker:
    def __init__(self):self.state=None;self.last_time=None
    def analyze(self,frame,t):
        if self.last_time is not None and (t<=self.last_time or t-self.last_time>.2):self.state=None
        self.last_time=t
        r=base.analyze(frame)
        options=base._SCOPE.get('audit_options',[])
        _,_,ys,yellow=base._SCOPE['detect'](frame)
        white=dict((ys[i]/frame.shape[0],x) for i,x in options[0][1]) if options else {}
        if r['control_status']=='ready':
            # Independent model carries its fitted points; paired path carries measured points.
            self.state=(t,r,white)
            return r
        if self.state is None or not options or len(options)>64:return r
        saved,old,ow=self.state
        if t-saved>.15:return r
        shared=white.keys() & ow.keys()
        if len(shared)<8:return r
        shifts=np.array([white[y]-ow[y] for y in shared]);shift=float(np.median(shifts))
        if abs(shift)>4 or max(abs(shifts-shift))>2:return r
        points=[(y,x+white[y]-ow[y]) for y,x in old['points'] if y in shared]
        if len(points)<4:return r
        top=max(0,int(frame.shape[0]*.55)-6);supported=0;checked=0
        for y,x in points:
            candidates=base._SCOPE['segments'](yellow,round(y*frame.shape[0])-top)
            if candidates:
                checked+=1
                if min(abs(left-(2*x-white[y])) for left in candidates)<=4:supported+=1
        if supported<2 or supported/max(checked,1)<.8:return r
        result=base.control(points,frame.shape[1],'selected')
        if result['control_status']!='ready':return r
        result.update(points=points,target_source='temporal_estimated',pair_status='temporal_experimental')
        # Do not refresh state from an estimate; limit total age from independent observation.
        return result
