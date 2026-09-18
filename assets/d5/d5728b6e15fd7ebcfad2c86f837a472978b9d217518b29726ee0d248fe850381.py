import cv2,numpy as np
from pathlib import Path
from s2_preview_core import _SCOPE,analyze
root=Path('/Users/zhangweibin/Documents/Thesis/experiment_data/2026-09-07/20260907_154634_461086')
for name in ['000240','000265','000350','000395']:
 frame=cv2.imread(str(root/f'{name}_raw.jpg'));r=analyze(frame);h,w=frame.shape[:2];top=int(h*.55)
 white,yellow=_SCOPE['build_color_masks'](frame[top:]);v=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,2]
 print(name,'points',r['points'])
 for i,wx in r['chosen'].items():
  y=r['ys'][i];yc=_SCOPE['segments'](yellow,y-top)
  print(' y',y,'wx',wx,'yellow',yc)
  for yx in yc:
   if .15*w <= wx-yx <= .85*w:
    interior=v[y,max(0,int(yx)+3):max(0,int(wx)-3)]
    print('   pair',yx,wx,'width',wx-yx,'dark145',np.mean(interior<145),'dark120',np.mean(interior<120),'median',np.median(interior))
