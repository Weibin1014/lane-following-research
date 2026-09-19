#!/usr/bin/env python3
"""Capture one small image without importing or initialising any PWM driver."""

from datetime import datetime
from pathlib import Path
import argparse
import time

from picamera2 import Picamera2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Output JPEG path")
    args = parser.parse_args()

    output = args.output or Path("camera-tests") / f"camera_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)

    camera = Picamera2()
    config = camera.create_still_configuration(main={"size": (160, 120), "format": "RGB888"})
    camera.configure(config)
    try:
        camera.start()
        time.sleep(2.0)
        camera.capture_file(str(output))
    finally:
        camera.stop()
        camera.close()

    print(f"Saved camera image: {output.resolve()}")
    print("No PWM driver was imported or initialised.")


if __name__ == "__main__":
    main()

