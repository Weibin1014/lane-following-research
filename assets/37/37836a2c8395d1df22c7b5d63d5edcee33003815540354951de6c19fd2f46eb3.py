#!/usr/bin/env python3
"""
Color-based outer-lane detector for the indoor track.

The target lane is defined by:
  - outer white boundary line
  - inner yellow dashed line

The detector looks in the lower ROI, finds white/yellow mask pixels near the
bottom of the image, and estimates the target lane center between them.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def build_masks(roi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    white_mask = cv2.inRange(hsv, np.array([0, 0, 145]), np.array([179, 80, 255]))
    yellow_mask = cv2.inRange(hsv, np.array([15, 60, 80]), np.array([40, 255, 255]))

    kernel = np.ones((3, 3), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
    return white_mask, yellow_mask


def median_x_near_bottom(mask: np.ndarray, side: str, bottom_ratio: float) -> int | None:
    height, width = mask.shape[:2]
    y0 = int(height * bottom_ratio)
    band = mask[y0:height, :]

    ys, xs = np.where(band > 0)
    if xs.size < 8:
        return None

    if side == "left":
        xs = xs[xs < width * 0.65]
    elif side == "right":
        xs = xs[xs > width * 0.35]

    if xs.size < 8:
        return None
    return int(np.median(xs))


def detect_outer_lane(
    frame: np.ndarray,
    roi_top_ratio: float,
    lane_side: str,
    bottom_ratio: float,
    fallback_lane_width_ratio: float,
) -> dict:
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)
    roi = frame[roi_top:height, :]
    white_mask, yellow_mask = build_masks(roi)

    if lane_side == "left":
        white_side = "left"
        yellow_side = "right"
        fallback_sign = 1
    else:
        white_side = "right"
        yellow_side = "left"
        fallback_sign = -1

    white_x = median_x_near_bottom(white_mask, white_side, bottom_ratio)
    yellow_x = median_x_near_bottom(yellow_mask, yellow_side, bottom_ratio)
    fallback_lane_width = int(width * fallback_lane_width_ratio)

    if white_x is not None and yellow_x is not None:
        target_x = int((white_x + yellow_x) / 2)
    elif white_x is not None:
        target_x = white_x + fallback_sign * fallback_lane_width // 2
    elif yellow_x is not None:
        target_x = yellow_x - fallback_sign * fallback_lane_width // 2
    else:
        target_x = None

    if target_x is not None:
        target_x = max(0, min(width - 1, target_x))

    return {
        "roi": roi,
        "roi_top": roi_top,
        "white_mask": white_mask,
        "yellow_mask": yellow_mask,
        "white_x": white_x,
        "yellow_x": yellow_x,
        "target_x": target_x,
        "frame_center_x": width // 2,
    }


def draw_debug(frame: np.ndarray, result: dict) -> np.ndarray:
    debug = frame.copy()
    height, width = frame.shape[:2]
    roi_top = result["roi_top"]

    cv2.rectangle(debug, (0, roi_top), (width - 1, height - 1), (0, 255, 255), 2)
    cv2.line(debug, (result["frame_center_x"], roi_top), (result["frame_center_x"], height), (255, 0, 0), 2)

    if result["white_x"] is not None:
        cv2.line(debug, (result["white_x"], roi_top), (result["white_x"], height), (255, 255, 255), 2)
    if result["yellow_x"] is not None:
        cv2.line(debug, (result["yellow_x"], roi_top), (result["yellow_x"], height), (0, 255, 255), 2)
    if result["target_x"] is not None:
        cv2.line(debug, (result["target_x"], roi_top), (result["target_x"], height), (0, 0, 255), 2)

    white_bgr = cv2.cvtColor(result["white_mask"], cv2.COLOR_GRAY2BGR)
    yellow_bgr = cv2.cvtColor(result["yellow_mask"], cv2.COLOR_GRAY2BGR)
    yellow_bgr[:, :, 0] = 0
    mask_view = cv2.addWeighted(white_bgr, 0.7, yellow_bgr, 0.7, 0)
    mask_view = cv2.resize(mask_view, (width // 3, height // 3))
    debug[height - mask_view.shape[0] : height, 0 : mask_view.shape[1]] = mask_view

    error = None
    steering = 0.0
    if result["target_x"] is not None:
        error = result["target_x"] - result["frame_center_x"]
        steering = error / (width / 2)

    text = f"target={result['target_x']} white={result['white_x']} yellow={result['yellow_x']} steer={steering:+.2f}"
    cv2.putText(debug, text, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    return debug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Color-based outer lane detector")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--lane-side", choices=["left", "right"], default="left")
    parser.add_argument("--roi-top", type=float, default=0.55)
    parser.add_argument("--bottom-ratio", type=float, default=0.45)
    parser.add_argument("--fallback-lane-width", type=float, default=0.42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = cv2.imread(args.input)
    if frame is None:
        raise FileNotFoundError(args.input)

    result = detect_outer_lane(
        frame,
        roi_top_ratio=args.roi_top,
        lane_side=args.lane_side,
        bottom_ratio=args.bottom_ratio,
        fallback_lane_width_ratio=args.fallback_lane_width,
    )
    debug = draw_debug(frame, result)
    cv2.imwrite(args.output, debug)
    print(
        f"target={result['target_x']} white={result['white_x']} "
        f"yellow={result['yellow_x']} center={result['frame_center_x']}"
    )


if __name__ == "__main__":
    main()
