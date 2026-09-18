from PIL import Image,ImageDraw
from pathlib import Path
import csv
base=Path('/Users/zhangweibin/Documents/Thesis/reports/pixel_evaluation_2026-09-12')
r=list(csv.DictReader((base/'annotation_samples.csv').open()))
for trial in dict.fromkeys(x['trial'] for x in r):
 sheet=Image.new('RGB',(1000,1550),'white');d=ImageDraw.Draw(sheet)
 for j,row in enumerate(x for x in r if x['trial']==trial):
  im=Image.open(row['image']).convert('RGB');y=j*155
  sheet.paste(im,(0,y+20));d.text((0,y+3),trial+' #'+row['sample'],fill='black')
  strip=im.crop((0,68,160,89)).resize((800,105),Image.Resampling.NEAREST)
  sheet.paste(strip,(190,y+30))
  for x in range(0,160,10):
   xx=190+x*5;d.line((xx,y+20,xx,y+29),fill='black');d.text((xx,y+6),str(x),fill='black')
  d.text((163,y+77),'78>',fill='red')
  # row 78 lies 50 pixels down from crop start
  d.line((190,y+82,989,y+82),fill=(255,0,0),width=1)
 sheet.save(base/(trial+'_measurement_contact.png'))
