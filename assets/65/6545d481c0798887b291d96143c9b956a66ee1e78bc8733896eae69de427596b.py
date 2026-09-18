from pathlib import Path
import sys,tarfile,csv,json,hashlib
base=Path(__file__).resolve().parent
sys.path.insert(0,str(base/'deps'));sys.path.insert(0,str(base))
import cv2,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from s2_preview_core_local import analyze
archive=base.parents[1]/'experiment_data/2026-09-09/comparison_20260909_backup_110905.tar.gz'
rows=list(csv.DictReader((base/'frames.csv').open()))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
proof=[]
with tarfile.open(archive) as a:
 prefix='continuous_local_16s_results/20260909_105712_827635/'
 for number,label in [(30,'Straight section'),(104,'Left bend')]:
  for suffix in ['raw','debug']:
   n=f'{number:06d}_{suffix}.png';(base/n).write_bytes(a.extractfile(prefix+n).read())
  frame=cv2.imread(str(base/f'{number:06d}_raw.png'));debug=cv2.imread(str(base/f'{number:06d}_debug.png'))
  result=analyze(frame);row=rows[number-1]
  assert result['steering_pwm']==int(row['requested_steering']),(result,row)
  h,w=frame.shape[:2];top=max(0,int(h*.55)-6);context=max(0,top-3)
  # Match the final mask branch, including the white context rows.
  hsv=cv2.cvtColor(frame[context:],cv2.COLOR_BGR2HSV)
  white=cv2.inRange(hsv,np.array([0,0,145]),np.array([179,80,255]))
  white=cv2.morphologyEx(white,cv2.MORPH_OPEN,np.ones((1,3),np.uint8))[top-context:]
  hsv=cv2.cvtColor(frame[top:],cv2.COLOR_BGR2HSV)
  yellow=cv2.inRange(hsv,np.array([15,60,80]),np.array([40,255,255]))
  k=np.ones((3,3),np.uint8);yellow=cv2.morphologyEx(yellow,cv2.MORPH_OPEN,k);yellow=cv2.morphologyEx(yellow,cv2.MORPH_CLOSE,k)
  fig,axs=plt.subplots(2,2,figsize=(8.8,6.7))
  axs[0,0].imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),interpolation='nearest');axs[0,0].set_title('(a) Saved camera frame',loc='left')
  for ax,mask,title in [(axs[0,1],white,'(b) White mask · reconstructed'),(axs[1,0],yellow,'(c) Yellow mask · reconstructed')]:
   ax.set_facecolor('#e8e8e8');ax.imshow(mask,cmap='gray',vmin=0,vmax=255,extent=(-.5,w-.5,h-.5,top-.5),interpolation='nearest');ax.set_xlim(-.5,w-.5);ax.set_ylim(h-.5,-.5);ax.axhline(top-.5,color='#777',linewidth=.6);ax.text(80,25,'Outside processing region',ha='center',va='center',fontsize=10,color='#555');ax.set_title(title,loc='left')
  axs[1,1].imshow(cv2.cvtColor(debug,cv2.COLOR_BGR2RGB));axs[1,1].set_title('(d) Saved control overlay',loc='left')
  for ax in axs.flat:ax.set_xticks([]);ax.set_yticks([])
  fig.subplots_adjust(left=.025,right=.99,top=.94,bottom=.06,wspace=.065,hspace=.16)
  fig.text(.03,.015,f'{label} | Run 3 | Frame {number:06d} | Logged steering PWM {row["requested_steering"]}',fontsize=10)
  fig.savefig(base/f'figure_{number:06d}.png',dpi=240,facecolor='white');plt.close(fig)
  proof.append(dict(run='20260909_105712_827635',frame=number,elapsed_s=row['elapsed_s'],requested_throttle=row['requested_throttle'],requested_steering=row['requested_steering'],target_source=row['target_source'],replayed_pwm=result['steering_pwm'],opencv_replay_version=cv2.__version__,core_sha256=hashlib.sha256((base/'s2_preview_core_local.py').read_bytes()).hexdigest()))
(base/'figure_provenance.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
