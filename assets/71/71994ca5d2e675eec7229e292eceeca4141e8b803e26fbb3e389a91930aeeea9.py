"""Offline local direction fit; never interpreted as observed far target."""
import numpy as np
import s2_preview_core_independent as base

def analyze(frame):
 r=base.analyze(frame)
 if r['control_status']=='ready':return r
 points=[(y,x) for y,x in r.get('points',[]) if .55<=y<=.80]
 if len(points)<4:return r
 near,status=base.target(points,.65)
 if near is None:return r
 a=np.array(points);yy=a[:,0];xx=a[:,1]
 if np.ptp(yy)<.075:return r
 coeff=np.polyfit(yy,xx,1);res=xx-np.polyval(coeff,yy)
 if max(abs(res))>1.5:return r
 # Require well-constrained slope, with a half-pixel noise floor.
 noise=max(.5,float(np.sqrt(np.sum(res**2)/max(1,len(points)-2))))
 uncertainty=noise/np.sqrt(np.sum((yy-yy.mean())**2))
 pwm_uncertainty=150*1.5*.1*uncertainty/(frame.shape[1]/2)
 if pwm_uncertainty>8:return r
 offset=(near-frame.shape[1]/2)/(frame.shape[1]/2)
 preview=float(np.clip(offset-1.5*.1*coeff[0]/(frame.shape[1]/2),-1,1))
 out=dict(r);out.update(control_status='ready',target_source='direction_estimated',near_x=near,near_status=status,near_offset=offset,preview_error=preview,steering_pwm=int(round(365-75*float(np.clip(preview/.5,-1,1)))),direction_uncertainty_pwm=pwm_uncertainty)
 return out

_SCOPE=base._SCOPE
control=base.control
