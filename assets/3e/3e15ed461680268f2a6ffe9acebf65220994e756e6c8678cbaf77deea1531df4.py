import ast
import csv
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

base = Path("offline_results/20260907_124734")
source = (base / "source_snapshot.py").read_text()
nodes = [
    n for n in ast.parse(source).body
    if isinstance(n, ast.FunctionDef)
    and n.name == "build_color_masks"
]
assert len(nodes) == 1
scope = {"cv2": cv2, "np": np}
exec(compile(ast.Module(body=nodes, type_ignores=[]),
             "<vision-only>", "exec"), scope)

with (base / "results.csv").open(newline="") as f:
    excluded = {Path(row["image"]).name for row in csv.DictReader(f)}

import random
pool = sorted(
    p for p in Path("data/images").glob("*.jpg")
    if p.name not in excluded
)
if len(pool) < 200:
    raise SystemExit("剩余图片不足200张")
paths = sorted(random.Random(20260907).sample(pool, 200))

output = Path("offline_results") / (
    "validation_v2_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
output.mkdir(parents=True)
(output / "test_script.py").write_text(Path(__file__).read_text())

def segments(mask, y):
    band = mask[max(0, y-2):min(mask.shape[0], y+3)]
    xs = np.flatnonzero(np.count_nonzero(band, axis=0) >= 2)
    if not len(xs):
        return []
    groups = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
    return [
        float(g.mean()) for g in groups
        if 2 <= len(g) <= mask.shape[1] * 0.18
    ]

# 从近处向远处，每隔画面高度的5%取样。
ratios = np.arange(0.90, 0.549, -0.05)
totals = {"selected": 0, "uncertain": 0, "no_track": 0}
center_frames = 0
failed = 0

with (output / "results.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "image", "track_status", "height_ratio",
        "white_x", "yellow_x", "center_x"
    ])

    for path in paths:
        frame = cv2.imread(str(path))
        if frame is None:
            failed += 1
            continue

        h, w = frame.shape[:2]
        top = int(h * 0.55)
        white, yellow = scope["build_color_masks"](frame[top:])
        ys = [max(top, int(round(h * r))) for r in ratios]
        candidates = [segments(white, y-top) for y in ys]

        # 动态规划：寻找跨高度连续的白色候选路径。
        # 允许跳过一条横带；参数仅用于离线诊断。
        yellow_candidates = [
            segments(yellow, y-top) for y in ys
        ]

        def pair_support(i, x):
            possible = [
                left for left in yellow_candidates[i]
                if 0.15*w <= x-left <= 0.85*w
            ]
            # 黄色虚线缺失时不扣分；唯一配对提供少量支持。
            return 0.35 if len(possible) == 1 else 0.0

        states = {}
        for i, xs in enumerate(candidates):
            for j, x in enumerate(xs):
                support = pair_support(i, x)
                best = (1.0 + support, [(i, x)])
                for gap in (1, 2):
                    prev = i-gap
                    if prev < 0:
                        continue
                    for k, old_x in enumerate(candidates[prev]):
                        if abs(x-old_x) > 0.14*w*gap:
                            continue
                        score, track = states[(prev, k)]
                        score += 1 - 0.25*abs(x-old_x)/(0.14*w*gap)
                        score += support
                        score -= 0.15*(gap-1)

                        # 比较相邻段的横向变化，抑制突然转折。
                        # 不要求白线必须是直线。
                        if len(track) >= 2:
                            earlier_i, earlier_x = track[-2]
                            old_step = (
                                (old_x-earlier_x) / (prev-earlier_i)
                            )
                            new_step = (x-old_x) / gap
                            score -= (
                                0.8 * abs(new_step-old_step) / (0.14*w)
                            )
                        if score > best[0]:
                            best = (score, track+[(i, x)])
                states[(i, j)] = best

        options = sorted(states.values(), key=lambda t: t[0], reverse=True)
        options = [
            item for item in options
            if len(item[1]) >= 5
            and item[1][-1][0]-item[1][0][0] >= 4
        ]

        status = "no_track"
        chosen = {}
        if options:
            score, track = options[0]
            chosen = dict(track)
            status = "selected"
            # 分数接近且位置明显不同的路径视为不确定。
            for other_score, other_track in options[1:]:
                if score-other_score > 0.75:
                    break
                other = dict(other_track)
                shared = sorted(chosen.keys() & other.keys())
                if len(shared) >= 3:
                    separation = np.median([
                        abs(chosen[i]-other[i]) for i in shared
                    ])
                    if separation > 0.12*w:
                        status = "uncertain"
                        chosen = {}
                        break

        totals[status] += 1
        view = cv2.resize(frame, (w*4, h*4))
        centers = 0

        for i, y in enumerate(ys):
            cv2.line(view, (0, y*4), (w*4-1, y*4),
                     (80, 80, 80), 1)
            for x in candidates[i]:
                cv2.circle(view, (round(x*4), y*4),
                           3, (140, 140, 140), -1)

            wx = chosen.get(i)
            yx = ""
            center = ""
            if wx is not None:
                cv2.circle(view, (round(wx*4), y*4),
                           5, (255, 255, 0), -1)
                possible = [
                    x for x in segments(yellow, y-top)
                    if 0.15*w <= wx-x <= 0.85*w
                ]
                for x in possible:
                    cv2.circle(view, (round(x*4), y*4),
                               4, (0, 255, 255), -1)
                if len(possible) == 1:
                    yx = possible[0]
                    center = (wx+yx)/2
                    centers += 1
                    cv2.circle(view, (round(center*4), y*4),
                               5, (0, 0, 255), -1)

            writer.writerow([
                path.name, status, round(float(ratios[i]), 2),
                wx if wx is not None else "", yx, center
            ])

        if centers:
            center_frames += 1
        cv2.putText(
            view, f"{status} centers={centers}",
            (10, 24), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (0, 255, 0), 2
        )
        if not cv2.imwrite(str(output/path.name), view):
            raise RuntimeError(f"保存失败: {path.name}")

print("测试图片:", len(paths))
print("读取失败:", failed)
print("选出连续白线:", totals["selected"])
print("白线存在歧义:", totals["uncertain"])
print("未找到足够连续的白线:", totals["no_track"])
print("至少有一个候选中心的图片:", center_frames)
print("以上均为候选统计，不是准确率")
print("结果目录:", output.resolve())
