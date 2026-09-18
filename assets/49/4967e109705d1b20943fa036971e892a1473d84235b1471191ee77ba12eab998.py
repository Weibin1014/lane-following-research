import ast
import csv
import textwrap
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from picamera2 import Picamera2

# 只提取视觉函数和检测代码，不执行离线脚本的顶层代码。
v4 = Path("offline_continuity_v4.py").read_text()
mask_source = Path(
    "offline_results/20260907_124734/source_snapshot.py"
).read_text()
old = "    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)"
assert mask_source.count(old) == 1
mask_source = mask_source.replace(old, "    # White closing disabled")

scope = {"cv2": cv2, "np": np}
for source, names in [
    (mask_source, {"build_color_masks"}),
    (v4, {"segments", "white_segments"}),
]:
    nodes = [
        n for n in ast.parse(source).body
        if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    assert {n.name for n in nodes} == names
    exec(compile(ast.Module(body=nodes, type_ignores=[]),
                 "<vision-functions>", "exec"), scope)

start_marker = "        h, w = frame.shape[:2]"
end_marker = "        totals[status] += 1"
assert v4.count(start_marker) == 1
assert v4.count(end_marker) == 1
block = v4.split(start_marker, 1)[1].split(end_marker, 1)[0]
block = textwrap.dedent(start_marker + block)
function = (
    "def detect(frame):\n"
    + textwrap.indent(block, "    ")
    + "\n    return status, chosen, ys, yellow\n"
)
scope["ratios"] = np.arange(0.90, 0.549, -0.05)
scope["scope"] = scope
exec(compile(function, "<vision-detection>", "exec"), scope)

out = Path("realtime_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
out.mkdir(parents=True)
(out / "script.py").write_text(Path(__file__).read_text())
(out / "v4_snapshot.py").write_text(v4)
(out / "mask_snapshot.py").write_text(mask_source)

counts = Counter()
processing = []
frames = 0
camera = Picamera2()
started = False
elapsed = 0.0

try:
    config = camera.create_video_configuration(
        main={"size": (160, 120), "format": "RGB888"},
        controls={"FrameRate": 20},
        buffer_count=4,
        queue=False,
    )
    camera.configure(config)
    (out / "camera_config.txt").write_text(str(camera.camera_configuration()))
    camera.start()
    started = True
    time.sleep(2)

    print("开始30秒纯视觉测试；Ctrl+C可提前结束。", flush=True)
    begin = time.perf_counter()
    next_save = 0.0

    with (out / "frames.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "frame", "elapsed_s", "capture_wait_ms",
            "processing_ms", "track_status", "target_status", "offset"
        ])

        while time.perf_counter() - begin < 30:
            capture_start = time.perf_counter()
            frame = camera.capture_array("main")
            process_start = time.perf_counter()
            capture_ms = (process_start-capture_start)*1000

            track_status, chosen, ys, yellow = scope["detect"](frame)
            h, w = frame.shape[:2]
            top = int(h*0.55)
            points = []

            for i, wx in chosen.items():
                possible = [
                    x for x in scope["segments"](yellow, ys[i]-top)
                    if 0.15*w <= wx-x <= 0.85*w
                ]
                if len(possible) == 1:
                    points.append((ys[i]/h, (wx+possible[0])/2))
            points.sort()

            target = None
            target_status = "unavailable"
            exact = [x for y, x in points if abs(y-0.65) < 1e-6]
            if exact:
                target = exact[0]
                target_status = "direct"
            else:
                above = [(y, x) for y, x in points if y < 0.65]
                below = [(y, x) for y, x in points if y > 0.65]
                if above and below:
                    y0, x0 = above[-1]
                    y1, x1 = below[0]
                    if y1-y0 <= 0.15+1e-6:
                        target = x0+(0.65-y0)/(y1-y0)*(x1-x0)
                        target_status = "interpolated"

            offset = None if target is None else (target-w/2)/(w/2)
            process_ms = (time.perf_counter()-process_start)*1000
            elapsed = time.perf_counter()-begin
            processing.append(process_ms)
            counts[target_status] += 1
            frames += 1
            writer.writerow([
                frames, elapsed, capture_ms, process_ms,
                track_status, target_status,
                "" if offset is None else offset
            ])

            # 每秒保存一张原图和一张诊断图。
            if elapsed >= next_save:
                next_save = elapsed+1
                view = cv2.resize(frame, (640, 480))
                for i, wx in chosen.items():
                    cv2.circle(view, (round(wx*4), ys[i]*4),
                               4, (255, 255, 0), -1)
                for y, x in points:
                    cv2.circle(view, (round(x*4), round(y*h)*4),
                               4, (0, 0, 255), -1)
                cv2.line(view, (0, 312), (639, 312), (255, 0, 0), 1)
                cv2.line(view, (320, 0), (320, 479), (255, 255, 0), 1)
                if target is not None:
                    cv2.circle(view, (round(target*4), 312),
                               9, (0, 255, 0), 2)
                label = f"{track_status} {target_status}"
                cv2.putText(view, label, (8, 22),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 1)
                for suffix, image in [("raw", frame), ("debug", view)]:
                    if not cv2.imwrite(
                        str(out / f"{frames:06d}_{suffix}.jpg"), image
                    ):
                        raise RuntimeError("截图保存失败")
                print(
                    f"{elapsed:.1f}s {label} "
                    f"offset={offset} process={process_ms:.1f}ms",
                    flush=True
                )
        elapsed = time.perf_counter()-begin

except KeyboardInterrupt:
    print("\n已提前停止。")
finally:
    try:
        if started:
            camera.stop()
    finally:
        camera.close()

print("处理帧数:", frames)
print("目标状态:", dict(counts))
if processing:
    print("视觉处理耗时中位数(ms):", round(float(np.median(processing)), 2))
    print("视觉处理耗时95分位(ms):",
          round(float(np.percentile(processing, 95)), 2))
if elapsed > 0:
    print("循环吞吐率(帧/秒):", round(frames/elapsed, 2))
print("结果目录:", out.resolve())
