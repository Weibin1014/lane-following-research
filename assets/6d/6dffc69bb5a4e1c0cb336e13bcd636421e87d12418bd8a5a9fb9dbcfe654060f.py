"""Independent, visually guided draft annotations; not human ground truth.
Fixed row y=78. White-line centre visually estimated; yellow-line centre read
from pixels within a visually selected band. No controller estimates imported.
"""
from pathlib import Path
import csv,json,math,statistics
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/pixel_evaluation_2026-09-12'
# Approximate positions selected by visual inspection of original images and
# 5x nearest-neighbour measurement strips. Used only to locate correct marking.
seeds={
'CNN_03':[(39,120.5),(32,111),(27,105),(19,101),(25,107.5),(21,100.5),(40,120.5),(8,79),(27,112),(24,104.5)],
'CNN_01R1':[(35,118),(27,104),(19,101),(15,92),(18,100),(10,84),(25,109),(19,100),(13,95),(21,102)],
'CNN_02R1':[(37,119),(34,117),(26,104),(18,100),(24,103),(37,120),(27,109),(15,94),(17,102),(23,103)],
'OpenCV_02':[(44,125),(39,121),(39,118.5),(36,119),(42,126.5),(35,119),(37,118),(45,128.5),(36,122),(32,118)],
'OpenCV_03':[(44,125.5),(40,119.5),(39,118.5),(37,122),(41,119),(36,118),(39,121),(45,121),(29,117),(39,122.5)],
'OpenCV_01R1':[(39,121),(37,117),(33,116),(36,122.5),(43,120),(32,119),(33,117),(39,128),(32,120),(28,118)]}
rows=list(csv.DictReader((OUT/'annotation_samples.csv').open()))
# Direct measurement only; no interpolation, extrapolation, or replacement.
# Borderline dash tips/gaps marked unmeasurable following visual inspection.
missing={'CNN_03':{2,5,6,9},'CNN_01R1':{2,3,4},'CNN_02R1':{2,5,7,8,10},'OpenCV_02':{2,4,7,9,10},'OpenCV_03':{5,6,7,8},'OpenCV_01R1':{3,5,6,7,10}}
measured=[]
for r in rows:
 trial=r['trial'];i=int(r['sample']);lx,rx=seeds[trial][i-1]
 r.update(measurement_y=78,left_x='',right_x=rx,status='unmeasurable' if i in missing[trial] else 'draft_measured',note='yellow dash gap or ambiguous dash tip at y=78' if i in missing[trial] else 'AI-assisted visual annotation, not human-verified ground truth',lane_center_x='',signed_error_px='',abs_error_px='',squared_error_px2='')
 if r['status']=='draft_measured':
  # Refine yellow stripe centre using local chromatic contrast only at y=78.
  a=np.array(Image.open(r['image']).convert('RGB'),dtype=float)[78]
  lo=max(0,lx-10);hi=min(160,lx+11)
  score=np.minimum(a[lo:hi,0],a[lo:hi,1])-a[lo:hi,2]
  keep=np.flatnonzero(score>=max(40,float(score.max())*.6))+lo
  if len(keep)<2:
   r.update(status='unmeasurable',note='insufficient yellow evidence on fixed row')
  else:
   # Candidate band is visually selected; midpoint of paint span defines boundary.
   left=(float(keep[0])+float(keep[-1]))/2
   center=(left+rx)/2;e=center-80
   r.update(left_x=left,lane_center_x=center,signed_error_px=e,abs_error_px=abs(e),squared_error_px2=e*e)
 measured.append(r)
fields=list(measured[0])
with (OUT/'pixel_annotations_draft.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(measured)
(OUT/'pixel_annotations_draft.json').write_text(json.dumps(measured,indent=2)+'\n')
summary=[]
for trial in seeds:
 rr=[r for r in measured if r['trial']==trial];v=[r for r in rr if r['status']=='draft_measured'];errors=[r['signed_error_px'] for r in v]
 mse=statistics.mean(e*e for e in errors)
 summary.append(dict(trial=trial,selected=10,measured=len(v),unmeasurable=10-len(v),mse_px2=mse,rmse_px=math.sqrt(mse),mae_px=statistics.mean(abs(e) for e in errors),status='draft conditional-on-visible-markings estimate'))
 # Review sheet: all 10 samples, including unavailable ones.
 sheet=Image.new('RGB',(1000,1550),'white');d=ImageDraw.Draw(sheet)
 for j,r in enumerate(rr):
  y=j*155;im=Image.open(r['image']).convert('RGB');sheet.paste(im,(0,y+20))
  d.text((0,y+3),trial+' #'+r['sample'],fill='black')
  strip=im.crop((0,68,160,89)).resize((800,105),Image.Resampling.NEAREST);sheet.paste(strip,(190,y+30))
  d.line((190,y+82,989,y+82),fill=(190,190,190))
  d.line((590,y+30,590,y+135),fill='blue',width=2)
  if r['status']=='draft_measured':
   for val,col in [(r['left_x'],'orange'),(r['right_x'],'green'),(r['lane_center_x'],'red')]:
    x=190+round(val*5);d.ellipse((x-4,y+78,x+4,y+86),outline=col,width=2)
   label=f"L={r['left_x']:.1f}, R={r['right_x']:.1f}, e={r['signed_error_px']:.2f} px (draft)"
  else: label='UNMEASURABLE: '+r['note']
  d.text((190,y+7),label,fill='black')
 sheet.save(OUT/(trial+'_annotated_review.png'))
(OUT/'pixel_summary_draft.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));print('TOTAL MEASURED',sum(x['measured'] for x in summary))
