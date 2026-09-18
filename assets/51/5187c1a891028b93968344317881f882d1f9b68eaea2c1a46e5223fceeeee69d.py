import numpy as np
import local_geometry_candidate as m
original=m.base.analyze;detect=m.base._SCOPE['detect'];segments=m.base._SCOPE['segments']
try:
    m.base.analyze=lambda frame:dict(control_status='unavailable')
    def run(heights,centers,pixels=0,count=1):
        ys=[round(y*120) for y in heights]
        m.base._SCOPE['audit_options']=[(1,[(i,x+40) for i,x in enumerate(centers)])]*count
        m.base._SCOPE['detect']=lambda frame:('selected',{},ys,None)
        lookup={y-60:x-40 for y,x in zip(ys,centers)}
        m.base._SCOPE['segments']=lambda yellow,y:[lookup[y]]
        return m.analyze(np.full((120,160,3),pixels,dtype=np.uint8))
    assert run([.55,.6,.65],[80,80,80])['control_status']=='ready'
    assert run([.55,.6],[80,80])['control_status']=='unavailable'
    assert run([.75,.8,.85],[80,80,80])['control_status']=='unavailable'
    assert run([.55,.6,.65],[80,90,80])['control_status']=='unavailable'
    assert run([.55,.6,.65],[80,80,80],255)['control_status']=='unavailable'
    assert run([.55,.6,.65],[80,80,80],count=65)['control_status']=='unavailable'
    print('PASS valid fit, insufficient points, excessive extrapolation, nonlinearity, bright interior, candidate cap')
finally:
    m.base.analyze=original;m.base._SCOPE['detect']=detect;m.base._SCOPE['segments']=segments
