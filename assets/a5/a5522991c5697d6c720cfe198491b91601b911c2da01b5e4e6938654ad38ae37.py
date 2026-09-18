#!/usr/bin/env python3
"""
Run the OpenCV lane-following baseline directly on the Raspberry Pi car.

This is a cautious test script:
  - camera frames are processed with ROI + Canny + Hough
  - steering is generated from estimated lane-center error
  - throttle is a fixed low PWM value
  - throttle is stopped if lane detection is lost
  - Ctrl+C sends stopped throttle and centered steering
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np
from Adafruit_PCA9685 import PCA9685
from picamera2 import Picamera2


STEERING_LEFT_PWM = 440
STEERING_CENTER_PWM = 350
STEERING_RIGHT_PWM = 290
THROTTLE_STOPPED_PWM = 370


def preprocess(frame: np.ndarray, roi_top_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)
    roi = frame[roi_top:height, 0:width]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 160)
    return roi, edges


def build_color_masks(roi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
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
    ys, xs = np.where(mask[y0:height, :] > 0)
    if xs.size < 8:
        return None
    if side == "left":
        xs = xs[xs < width * 0.65]
    elif side == "right":
        xs = xs[xs > width * 0.35]
    if xs.size < 8:
        return None
    return int(np.median(xs))


def detect_outer_lane_color(
    frame: np.ndarray,
    roi_top_ratio: float,
    lane_side: str,
    bottom_ratio: float,
    fallback_lane_width_ratio: float,
    target_offset_px: int,
) -> tuple[int | None, int, dict]:
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)
    roi = frame[roi_top:height, :]
    white_mask, yellow_mask = build_color_masks(roi)

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
        target_x += target_offset_px
        target_x = max(0, min(width - 1, target_x))

    debug_info = {
        "roi_top": roi_top,
        "white_mask": white_mask,
        "yellow_mask": yellow_mask,
        "white_x": white_x,
        "yellow_x": yellow_x,
    }
    detected_count = int(white_x is not None) + int(yellow_x is not None)
    return target_x, detected_count, debug_info


def detect_lines(edges: np.ndarray) -> np.ndarray | None:
    return cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=35,
        minLineLength=35,
        maxLineGap=25,
    )


def estimate_lane_center(lines: np.ndarray | None, width: int, height: int) -> tuple[int | None, int]:
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

    return max(0, min(width - 1, lane_center)), len(lines)


def compute_steering(lane_center_x: int | None, frame_center_x: int, width: int, gain: float) -> float:
    if lane_center_x is None:
        return 0.0
    error_px = lane_center_x - frame_center_x
    normalized_error = error_px / (width / 2)
    return float(np.clip(gain * normalized_error, -1.0, 1.0))


def draw_debug(
    frame: np.ndarray,
    roi_top_ratio: float,
    lines: np.ndarray | None,
    lane_center_x: int | None,
    steering: float,
    throttle_pwm: int,
    line_count: int,
) -> np.ndarray:
    debug = frame.copy()
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)
    frame_center_x = width // 2

    cv2.rectangle(debug, (0, roi_top), (width - 1, height - 1), (0, 255, 255), 2)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(debug, (x1, y1 + roi_top), (x2, y2 + roi_top), (0, 255, 0), 2)

    cv2.line(debug, (frame_center_x, roi_top), (frame_center_x, height), (255, 0, 0), 2)
    if lane_center_x is not None:
        cv2.line(debug, (lane_center_x, roi_top), (lane_center_x, height), (0, 0, 255), 2)

    text = f"steer={steering:+.2f} throttle={throttle_pwm} lines={line_count}"
    cv2.putText(debug, text, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    return debug


def draw_color_debug(
    frame: np.ndarray,
    debug_info: dict,
    target_x: int | None,
    steering: float,
    throttle_pwm: int,
    detected_count: int,
) -> np.ndarray:
    debug = frame.copy()
    height, width = frame.shape[:2]
    roi_top = debug_info["roi_top"]
    frame_center_x = width // 2

    cv2.rectangle(debug, (0, roi_top), (width - 1, height - 1), (0, 255, 255), 2)
    cv2.line(debug, (frame_center_x, roi_top), (frame_center_x, height), (255, 0, 0), 2)
    if debug_info["white_x"] is not None:
        cv2.line(debug, (debug_info["white_x"], roi_top), (debug_info["white_x"], height), (255, 255, 255), 2)
    if debug_info["yellow_x"] is not None:
        cv2.line(debug, (debug_info["yellow_x"], roi_top), (debug_info["yellow_x"], height), (0, 255, 255), 2)
    if target_x is not None:
        cv2.line(debug, (target_x, roi_top), (target_x, height), (0, 0, 255), 2)

    white_bgr = cv2.cvtColor(debug_info["white_mask"], cv2.COLOR_GRAY2BGR)
    yellow_bgr = cv2.cvtColor(debug_info["yellow_mask"], cv2.COLOR_GRAY2BGR)
    yellow_bgr[:, :, 0] = 0
    mask_view = cv2.addWeighted(white_bgr, 0.7, yellow_bgr, 0.7, 0)
    mask_view = cv2.resize(mask_view, (width // 3, height // 3))
    debug[height - mask_view.shape[0] : height, 0 : mask_view.shape[1]] = mask_view

    text = f"target={target_x} steer={steering:+.2f} throttle={throttle_pwm} marks={detected_count}"
    cv2.putText(debug, text, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
    return debug


def steering_to_pwm(steering: float, max_steering: float, center_pwm: int) -> int:
    steering = float(np.clip(steering, -max_steering, max_steering))
    if steering < 0:
        return int(center_pwm + (-steering / max_steering) * (STEERING_LEFT_PWM - center_pwm))
    if steering > 0:
        return int(center_pwm + (steering / max_steering) * (STEERING_RIGHT_PWM - center_pwm))
    return center_pwm


def set_pwm(pwm: PCA9685, steering_pwm: int, throttle_pwm: int) -> None:
    pwm.set_pwm(1, 0, steering_pwm)
    pwm.set_pwm(0, 0, throttle_pwm)


def safe_set_pwm(
    pwm: PCA9685,
    steering_pwm: int,
    throttle_pwm: int,
    retries: int = 2,
) -> PCA9685:
    for attempt in range(retries + 1):
        try:
            set_pwm(pwm, steering_pwm, throttle_pwm)
            return pwm
        except OSError as exc:
            print(f"I2C write failed attempt {attempt + 1}/{retries + 1}: {exc}")
            time.sleep(0.05)
            pwm = init_pwm_with_retry(retries=2, delay=0.1)
    return pwm


def init_pwm_with_retry(retries: int = 5, delay: float = 0.5) -> PCA9685:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            pwm = PCA9685(address=0x40, busnum=1)
            pwm.set_pwm_freq(60)
            return pwm
        except OSError as exc:
            last_error = exc
            print(f"PCA9685 init failed attempt {attempt}/{retries}: {exc}")
            time.sleep(delay)
    raise RuntimeError("Could not initialize PCA9685 on I2C bus 1 address 0x40") from last_error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenCV lane follower on Raspberry Pi car")
    parser.add_argument("--detector", choices=["hough", "color"], default="color")
    parser.add_argument("--lane-side", choices=["left", "right"], default="left")
    parser.add_argument("--throttle-pwm", type=int, default=400, help="Low forward throttle PWM")
    parser.add_argument("--duration", type=float, default=20.0, help="Maximum run time in seconds")
    parser.add_argument("--roi-top", type=float, default=0.55)
    parser.add_argument("--bottom-ratio", type=float, default=0.45)
    parser.add_argument("--fallback-lane-width", type=float, default=0.42)
    parser.add_argument("--target-offset-px", type=int, default=0, help="Shift target lane center left/right in pixels")
    parser.add_argument("--steering-gain", type=float, default=0.8)
    parser.add_argument("--max-steering", type=float, default=0.7)
    parser.add_argument("--steering-center-pwm", type=int, default=STEERING_CENTER_PWM)
    parser.add_argument("--throttle-ramp", type=float, default=2.0, help="Seconds to ramp from stopped to target throttle")
    parser.add_argument("--loop-hz", type=float, default=20.0, help="Control loop rate limit")
    parser.add_argument("--invert-steering", action="store_true", help="Reverse OpenCV steering direction")
    parser.add_argument("--debug-dir", help="Optional directory for saved debug frames")
    parser.add_argument("--debug-every", type=int, default=10, help="Save one debug frame every N frames")
    parser.add_argument("--lost-stop", action="store_true", default=True, help="Stop throttle when lane is lost")
    parser.add_argument("--width", type=int, default=160)
    parser.add_argument("--height", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pwm = init_pwm_with_retry()
    pwm = safe_set_pwm(pwm, args.steering_center_pwm, THROTTLE_STOPPED_PWM)

    camera = Picamera2()
    config = camera.create_preview_configuration(
        main={"size": (args.width, args.height), "format": "BGR888"}
    )
    camera.configure(config)
    camera.start()
    time.sleep(1.0)

    print("OpenCV car test starting in 3 seconds. Keep one hand ready to lift/stop the car.")
    for remaining in (3, 2, 1):
        print(f"{remaining}...")
        time.sleep(1.0)

    start = time.perf_counter()
    frame_count = 0
    total_frames = 0
    last_log = start
    debug_dir = Path(args.debug_dir) if args.debug_dir else None
    if debug_dir:
        debug_dir.mkdir(parents=True, exist_ok=True)

    try:
        while time.perf_counter() - start < args.duration:
            loop_start = time.perf_counter()
            frame = camera.capture_array()
            lines = None
            debug_info = None
            if args.detector == "color":
                lane_center_x, line_count, debug_info = detect_outer_lane_color(
                    frame,
                    args.roi_top,
                    args.lane_side,
                    args.bottom_ratio,
                    args.fallback_lane_width,
                    args.target_offset_px,
                )
            else:
                roi, edges = preprocess(frame, args.roi_top)
                lines = detect_lines(edges)
                lane_center_x, line_count = estimate_lane_center(lines, roi.shape[1], roi.shape[0])
            steering = compute_steering(lane_center_x, frame.shape[1] // 2, frame.shape[1], args.steering_gain)
            if args.invert_steering:
                steering *= -1.0
            steering_pwm = steering_to_pwm(steering, args.max_steering, args.steering_center_pwm)
            if lane_center_x is not None:
                run_elapsed = time.perf_counter() - start
                ramp = 1.0 if args.throttle_ramp <= 0 else min(1.0, run_elapsed / args.throttle_ramp)
                throttle_pwm = int(THROTTLE_STOPPED_PWM + (args.throttle_pwm - THROTTLE_STOPPED_PWM) * ramp)
            else:
                throttle_pwm = THROTTLE_STOPPED_PWM

            pwm = safe_set_pwm(pwm, steering_pwm, throttle_pwm)
            frame_count += 1
            total_frames += 1

            if debug_dir and total_frames % args.debug_every == 0:
                if args.detector == "color":
                    debug = draw_color_debug(
                        frame, debug_info, lane_center_x, steering,
                        throttle_pwm, line_count
                    )
                else:
                    debug = draw_debug(
                        frame, args.roi_top, lines, lane_center_x,
                        steering, throttle_pwm, line_count
                    )
                cv2.imwrite(str(debug_dir / f"frame_{total_frames:05d}.jpg"), debug)

            now = time.perf_counter()
            if now - last_log >= 1.0:
                fps = frame_count / (now - last_log)
                frame_count = 0
                last_log = now
                print(
                    f"fps={fps:.1f} steering={steering:+.2f} "
                    f"steer_pwm={steering_pwm} throttle_pwm={throttle_pwm} "
                    f"lane_center={lane_center_x} lines={line_count}"
                )

            elapsed = time.perf_counter() - loop_start
            target = 1.0 / args.loop_hz
            if elapsed < target:
                time.sleep(target - elapsed)
    except KeyboardInterrupt:
        print("Interrupted, stopping car.")
    finally:
        try:
            safe_set_pwm(pwm, args.steering_center_pwm, THROTTLE_STOPPED_PWM)
        except Exception as exc:
            print(f"Could not send final stop PWM: {exc}")
        camera.stop()
        camera.close()
        print("Car stopped.")


if __name__ == "__main__":
    main()
