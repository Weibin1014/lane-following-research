#!/usr/bin/env bash
set -u

ENV_DIR="${LANE_ENV_DIR:-$HOME/lane-env}"
PYTHON_BIN="$ENV_DIR/bin/python"

echo "=== Board and operating system ==="
tr -d '\0' </proc/device-tree/model 2>/dev/null || echo "Model unavailable"
echo
sed -n '1,8p' /etc/os-release 2>/dev/null || true

echo
echo "=== Python imports ==="
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing $PYTHON_BIN. Run scripts/01_prepare_pi.sh first."
else
  "$PYTHON_BIN" - <<'PY'
modules = ["cv2", "numpy", "picamera2", "Adafruit_PCA9685"]
for name in modules:
    try:
        module = __import__(name)
        version = getattr(module, "__version__", "installed")
        print(f"PASS  {name}: {version}")
    except Exception as exc:
        print(f"FAIL  {name}: {exc}")
PY
fi

echo
echo "=== Camera inventory ==="
if command -v rpicam-hello >/dev/null 2>&1; then
  rpicam-hello --list-cameras || true
elif command -v libcamera-hello >/dev/null 2>&1; then
  libcamera-hello --list-cameras || true
else
  echo "No rpicam-hello/libcamera-hello command found."
fi

echo
echo "=== I2C bus 1 (read-only scan) ==="
if command -v i2cdetect >/dev/null 2>&1; then
  i2cdetect -y 1 || true
  echo "The archived PCA9685 board should normally appear as 40."
else
  echo "i2cdetect is missing."
fi

echo
echo "System check complete. No PWM commands were sent."

