#!/usr/bin/env python3
"""
Simple OpenCV lane-following baseline for thesis experiments.

This script is designed for offline testing first. It can read a single image,
a video file, or a live camera index, then estimate a steering value from the
detected lane center.

Examples:
  python3 scripts/opencv_lane_detection.py --input track.jpg
  python3 scripts/opencv_lane_detection.py --input run.mp4
  python3 scripts/opencv_lane_detection.py --camera 0
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class LaneResult:
    steering: float
    lane_center_x: int | None
    frame_center_x: int
    error_px: int | None
    line_count: int
    fps: float


def preprocess(frame: np.ndarray, roi_top_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    """Crop the road area and create a Canny edge image."""
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)
    roi = frame[roi_top:height, 0:width]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 160)
    return roi, edges


def detect_lines(edges: np.ndarray) -> np.ndarray | None:
    """Detect lane-like line segments with probabilistic Hough transform."""
    return cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=35,
        minLineLength=35,
        maxLineGap=25,
    )


def estimate_lane_center(
    lines: np.ndarray | None,
    width: int,
    height: int,
) -> tuple[int | None, int]:
    """
    Estimate lane center using line intersections near the bottom of the ROI.

    The method separates left and right lane candidates by slope. If both sides
    are visible, the lane center is the midpoint. If only one side is visible,
    it estimates the center using a fixed lane width guess.
    """
    if lines is None:
        return None, 0

    left_x: list[int] = []
    right_x: list[int] = []
    y_eval = height - 1

    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0:
            continue

        slope = dy / dx
        if abs(slope) < 0.35:
            continue

        intercept = y1 - slope * x1
        x_at_bottom = int((y_eval - intercept) / slope)

        if x_at_bottom < 0 or x_at_bottom >= width:
            continue

        if slope < 0:
            left_x.append(x_at_bottom)
        else:
            right_x.append(x_at_bottom)

    lane_width_guess = int(width * 0.55)

    if left_x and right_x:
        lane_center = int((np.median(left_x) + np.median(right_x)) / 2)
    elif left_x:
        lane_center = int(np.median(left_x) + lane_width_guess / 2)
    elif right_x:
        lane_center = int(np.median(right_x) - lane_width_guess / 2)
    else:
        return None, len(lines)

    lane_center = max(0, min(width - 1, lane_center))
    return lane_center, len(lines)


def compute_steering(
    lane_center_x: int | None,
    frame_center_x: int,
    width: int,
    steering_gain: float,
) -> tuple[float, int | None]:
    """Convert lane-center error to a normalized steering command [-1, 1]."""
    if lane_center_x is None:
        return 0.0, None

    error_px = lane_center_x - frame_center_x
    normalized_error = error_px / (width / 2)
    steering = steering_gain * normalized_error
    steering = float(np.clip(steering, -1.0, 1.0))
    return steering, error_px


def draw_debug(
    frame: np.ndarray,
    roi: np.ndarray,
    edges: np.ndarray,
    lines: np.ndarray | None,
    roi_top_ratio: float,
    result: LaneResult,
) -> np.ndarray:
    """Create a visualization image for tuning and thesis screenshots."""
    debug = frame.copy()
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)

    cv2.rectangle(debug, (0, roi_top), (width - 1, height - 1), (0, 255, 255), 2)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(debug, (x1, y1 + roi_top), (x2, y2 + roi_top), (0, 255, 0), 2)

    cv2.line(debug, (result.frame_center_x, roi_top), (result.frame_center_x, height), (255, 0, 0), 2)

    if result.lane_center_x is not None:
        cv2.line(debug, (result.lane_center_x, roi_top), (result.lane_center_x, height), (0, 0, 255), 2)
        cv2.circle(debug, (result.lane_center_x, height - 25), 7, (0, 0, 255), -1)

    status = (
        f"steering={result.steering:+.2f} "
        f"error_px={result.error_px} "
        f"lines={result.line_count} "
        f"fps={result.fps:.1f}"
    )
    cv2.putText(debug, status, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    edges_bgr = cv2.resize(edges_bgr, (width // 3, height // 3))
    debug[height - edges_bgr.shape[0] : height, 0 : edges_bgr.shape[1]] = edges_bgr

    return debug


def process_frame(
    frame: np.ndarray,
    roi_top_ratio: float,
    steering_gain: float,
    fps: float,
) -> tuple[LaneResult, np.ndarray]:
    roi, edges = preprocess(frame, roi_top_ratio)
    lines = detect_lines(edges)
    lane_center_x, line_count = estimate_lane_center(lines, roi.shape[1], roi.shape[0])
    frame_center_x = frame.shape[1] // 2
    steering, error_px = compute_steering(lane_center_x, frame_center_x, frame.shape[1], steering_gain)

    result = LaneResult(
        steering=steering,
        lane_center_x=lane_center_x,
        frame_center_x=frame_center_x,
        error_px=error_px,
        line_count=line_count,
        fps=fps,
    )
    debug = draw_debug(frame, roi, edges, lines, roi_top_ratio, result)
    return result, debug


def run_image(path: Path, args: argparse.Namespace) -> None:
    frame = cv2.imread(str(path))
    if frame is None:
        raise FileNotFoundError(f"Cannot read image: {path}")

    result, debug = process_frame(frame, args.roi_top, args.steering_gain, fps=0.0)
    print(result)

    if args.output:
        cv2.imwrite(args.output, debug)

    if args.no_display:
        return

    cv2.imshow("Lane detection debug", debug)
    cv2.waitKey(0)


def run_stream(source: str | int, args: argparse.Namespace) -> None:
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video source: {source}")

    last_time = time.perf_counter()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        now = time.perf_counter()
        dt = now - last_time
        last_time = now
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps else 1.0 / dt

        result, debug = process_frame(frame, args.roi_top, args.steering_gain, fps=fps)
        print(
            f"steering={result.steering:+.3f}, "
            f"error_px={result.error_px}, "
            f"lines={result.line_count}, "
            f"fps={result.fps:.1f}"
        )

        if not args.no_display:
            cv2.imshow("Lane detection debug", debug)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break

    cap.release()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenCV lane detection baseline")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Path to an image or video file")
    source.add_argument("--camera", type=int, help="Camera index, for example 0")
    parser.add_argument("--roi-top", type=float, default=0.55, help="Top of ROI as frame-height ratio")
    parser.add_argument("--steering-gain", type=float, default=0.8, help="P-controller gain")
    parser.add_argument("--output", help="Optional output image path for single-image mode")
    parser.add_argument("--no-display", action="store_true", help="Do not open an OpenCV display window")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input:
        path = Path(args.input)
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
            run_image(path, args)
        else:
            run_stream(str(path), args)
    else:
        run_stream(args.camera, args)

    if not args.no_display:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
