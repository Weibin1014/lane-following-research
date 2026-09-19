#!/usr/bin/env bash
set -euo pipefail

ENV_DIR="${LANE_ENV_DIR:-$HOME/lane-env}"

echo "[1/4] Updating Raspberry Pi OS package lists"
sudo apt update

echo "[2/4] Installing camera, OpenCV, NumPy, Git, I2C and ZIP tools"
sudo apt install -y git unzip i2c-tools python3-venv python3-opencv \
  python3-numpy python3-picamera2

echo "[3/4] Creating Python environment at $ENV_DIR"
python3 -m venv --system-site-packages "$ENV_DIR"

echo "[4/4] Installing the PCA9685 Python library used by the archived project"
"$ENV_DIR/bin/python" -m pip install --upgrade pip
"$ENV_DIR/bin/python" -m pip install Adafruit-PCA9685

cat <<EOF

Preparation complete.

Next steps:
  1. Run: sudo raspi-config
  2. Open Interface Options and enable I2C.
  3. Reboot: sudo reboot
  4. Return to this folder and run: bash scripts/02_system_check.sh

This script did not initialise PWM or start a motor.
EOF

