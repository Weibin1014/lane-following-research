from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
p=Path('/Users/zhangweibin/Documents/Thesis/reports/pixel_evaluation_2026-09-12')
s=json.loads((p/'pixel_summary_draft.json').read_text());r=json.loads((p/'pixel_annotations_draft.json').read_text())
for x in s: assert x['measured']+x['unmeasurable']==10 and math.isclose(x['rmse_px']**2,x['mse_px2'])
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
for j,x in enumerate(s):
 ax.scatter(j,x['rmse_px'],s=90,color='#b45b24' if x['trial'].startswith('CNN') else '#187c87')
 ax.annotate(f"{x['rmse_px']:.1f} px\nn={x['measured']}/10",(j,x['rmse_px']),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
ax.set_xticks(range(6),[x['trial'] for x in s]);ax.set_ylim(0,27);ax.set_ylabel('RMSE (pixels)');ax.set_title('Draft estimates: measurable sampled frames only\nAI-assisted annotations; missing frames excluded, not zero-filled',fontsize=12);ax.grid(axis='y',alpha=.2)
fig.savefig(p/'rmse_draft.png',dpi=180);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
for ax,trial in zip(axes,['CNN_03','OpenCV_03']):
 row=next(x for x in r if x['trial']==trial and x['sample']=='4')
 ax.imshow(Image.open(row['image']));ax.axhline(78,color='white',ls='--',lw=1);ax.axvline(80,color='#3478f6',lw=1)
 ax.scatter([row['left_x'],row['right_x']],[78,78],color=['orange','lime'],s=35)
 ax.scatter([row['lane_center_x']],[78],color='red',s=35)
 ax.annotate('',xy=(80,86),xytext=(row['lane_center_x'],86),arrowprops={'arrowstyle':'<->','color':'red'})
 ax.set_title(f"{trial}, sample 4\nDraft e = {row['signed_error_px']:.1f} px")
 ax.set_xlabel('Original image x (pixels)');ax.set_ylabel('Original image y (pixels)');ax.set_xlim(0,159);ax.set_ylim(119,0)
fig.suptitle('Measurement example: y=78, image centre x=80\nOrange/green: marking centres; red: lane centre; blue: image centre',fontsize=12)
fig.savefig(p/'measurement_examples_draft.png',dpi=180);plt.close(fig)
text='''# 2026-09-12 像素偏差评价：AI辅助标注初稿

## 状态

六次选定试验的990张原始图片与150?条记录已备份；准确逐次数量见 six_run_audit.json。本报告只评价每次预先按时间均匀抽取的10张，共60张。34张可直接测量，26张无法直接测量。统计数值为AI辅助标注初稿，尚未由操作者独立复核，不是人工标注真值，也不是整圈完整误差。

论文主文件未修改。其他试次按用户要求不纳入本次统计，原始备份保留。

## 统一规则

- 原始图像160×120；固定零起始坐标 y=78（数组第79行），图像中心按既有约定 x=80。此规则由本次讨论确定，不声称导师明确指定了该行。按严格离散像素几何中心应为79.5；这里沿用用户确认的80，六次一致。
- 左边界位置定义为黄色车道分隔标线在该行的横向中心，右边界为右侧白色标线的横向中心，采用标线中心而非标线内边缘。车道中心=(left_x+right_x)/2；e=车道中心−80；MSE=mean(e²)，RMSE=sqrt(MSE)，MAE=mean(|e|)。MSE单位px²，其他为px。
- 抽帧按每次可用记录时间范围内10个等间隔目标时刻，选择最邻近的原图。OpenCV只从油门请求400的已保存帧中选取；CNN选定运行的已保存记录均为local_angle、用户油门0.375。使用时间索引不是赛道位置对齐，不能把相同序号称为同一物理地点。
- 不依据偏差大小替换图片，不读取OpenCV near_offset、near_x或识别红点作为评价真值。
- 若固定行处为黄色虚线间隙或不清晰端点，标为无法直接测量。未插值、外推、沿用上一帧、补零或替换样本。出界事件照实保留，未因驾驶表现剔除整次试验。

## 标注来源与可复核性

这是AI辅助的视觉标注，不是由用户或导师完成的人工标注。助手逐一查看全部60张原图缩略图和固定行的5倍最近邻放大条带，给出白色标线横坐标估计，并选择黄色标线附近的局部范围。对黄色标线可直接测量的样本，在该范围第78行用 min(R,G)−B 的颜色对比度提取标线：阈值=max(40,局部最大对比度×0.6)，取通过阈值的首末像素中点。该独立辅助规则同时应用两种方法，与车辆运行的HSV控制器不同，但仍会有颜色和阈值误差，不能称为无偏人工真值。白色标线坐标为视觉估计，未量化标注者误差。六张复核图已由助手查看，仍需操作者独立复核。

图中蓝色竖线是x=80，灰色水平线是y=78，橙点是黄色标线中心，绿点是白色标线中心，红点是两者中点。注意这些是本次评价标记，与车辆原识别图的颜色含义不同。

## 初步逐次结果

|试次|可测/抽样|无法测量|MSE(px²)|RMSE(px)|MAE(px)|
|---|---:|---:|---:|---:|---:|
'''
text=text.replace('与150?条记录','与150?条记录')
a=json.loads((p/'six_run_audit.json').read_text());text=text.replace('150?',str(sum(x['records'] for x in a)))
for x in s:text+=f"|{x['trial']}|{x['measured']}/10|{x['unmeasurable']}|{x['mse_px2']:.1f}|{x['rmse_px']:.1f}|{x['mae_px']:.1f}|\n"
text+='''
在本批可直接测量的样本中，OpenCV的初稿RMSE较小。不能据此给出显著性、整圈精度、厘米偏差、长期可靠性或速度优势结论。不可测帧共26/60，缺失与虚线位置和车辆姿态有关，未必随机；两种方法实际参与计算的样本数量也不同。这些统计只对可测样本成立。每次只有5–7张有效图像，连续帧也不是独立试验。

![逐次初稿RMSE](rmse_draft.png)

![测量示例](measurement_examples_draft.png)

## 全部样本复核图

'''
for trial in [x['trial'] for x in s]:text+=f'- [{trial}：全部10张，包括不可测样本]({trial}_annotated_review.png)\n'
text+='''
## 后续

1. 对上述叠加图核对白色/黄色标线位置及不可测标记；在 pixel_annotations_draft.csv 中保留修改依据。正式统计前需明确标注验证情况。
2. 26张不可测帧保留为缺失。如采用邻行插值补充，需要另行定义并验证统一规则，不能悄悄改变本次直接测量结果。
3. 正式论文应报告抽样规则、有效/缺失数、像素坐标约定、标注来源和限制。当前没有自动把这份初稿写入 Thesis_Main.docx。

计算与抽帧脚本在 experiments/pixel_evaluation_20260912 下，全部可追溯原图路径在 pixel_annotations_draft.csv。sha256.json是本地备份文件的校验清单，不代表已与树莓派逐文件比对哈希。
'''
(p/'像素偏差评价_初稿.md').write_text(text)
print(p/'像素偏差评价_初稿.md')

# Persistent review history
with (p/'像素偏差评价_初稿.md').open('a') as review_out:
    review_out.write('\n## 人工复核与修正记录\n\n')
    for review_file in sorted(p.glob('*review*.json')):
        entry=json.loads(review_file.read_text())
        review_out.write(f"- {entry.get('trial','')}: {entry.get('status',entry.get('correction_status',''))}；详情见 [{review_file.name}]({review_file.name})。\n")
