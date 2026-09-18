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
    paths = [Path(row["image"]) for row in csv.DictReader(f)]

output = Path("offline_results") / (
    "bands_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
output.mkdir(parents=True)
(output / "test_script.py").write_text(Path(__file__).read_text())

def segments(mask, y):
    # 在5像素高的横带中，至少两行出现颜色才算候选。
    band = mask[max(0, y - 2):min(mask.shape[0], y + 3)]
    xs = np.flatnonzero(np.count_nonzero(band, axis=0) >= 2)
    if not len(xs):
        return []
    groups = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
    # 暂时排除很细的噪点和很宽的色块。
    return [
        float(group.mean()) for group in groups
        if 2 <= len(group) <= mask.shape[1] * 0.18
    ]

counts = {"unique_pair": 0, "no_pair": 0, "ambiguous": 0}
failed = 0

with (output / "bands.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "image", "height_ratio", "yellow_candidates",
        "white_candidates", "status", "center_x"
    ])

    for path in paths:
        frame = cv2.imread(str(path))
        if frame is None:
            failed += 1
            continue

        h, w = frame.shape[:2]
        top = int(h * 0.55)
        white, yellow = scope["build_color_masks"](frame[top:])
        view = cv2.resize(frame, (w * 4, h * 4))

        for ratio in (0.60, 0.70, 0.80, 0.90):
            y = int(h * ratio)
            whites = segments(white, y - top)
            yellows = segments(yellow, y - top)

            # 只保留黄左白右、间距在暂定范围内的组合。
            # 这些范围只是诊断起点，仍需看图验证。
            pairs = [
                (left, right)
                for left in yellows for right in whites
                if 0.15 * w <= right - left <= 0.85 * w
            ]

            center = ""
            if len(pairs) == 1:
                status = "unique_pair"
                center = sum(pairs[0]) / 2
            elif not pairs:
                status = "no_pair"
            else:
                status = "ambiguous"
            counts[status] += 1

            cv2.line(view, (0, y * 4), (w * 4 - 1, y * 4),
                     (100, 100, 100), 1)
            for x in yellows:
                cv2.circle(view, (round(x * 4), y * 4),
                           5, (0, 255, 255), -1)
            for x in whites:
                cv2.circle(view, (round(x * 4), y * 4),
                           5, (255, 255, 0), -1)
            if center != "":
                cv2.circle(view, (round(center * 4), y * 4),
                           6, (0, 0, 255), -1)

            cv2.putText(
                view, f"{ratio:.2f} {status}", (4, y * 4 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 0), 1
            )
            writer.writerow([
                path.name, ratio, yellows, whites, status, center
            ])

        if not cv2.imwrite(str(output / path.name), view):
            raise RuntimeError(f"保存失败: {path.name}")

print("测试图片数:", len(paths))
print("读取失败:", failed)
print("横带统计（每张4条，不是图片准确率）:")
for name, count in counts.items():
    print(f"  {name}: {count}")
print("结果目录:", output.resolve())
