# Deployment and Usage Guide

This guide explains which download to choose, how to inspect the files, how to run the vision code without vehicle motion, and how to publish a copy of the research website.

## 1. Choose a package

- `01-key-findings.zip`: start here. It contains the three central reports, English reading editions, original Chinese records, and chart data.
- `02-experiment-data.zip`: use this for JSON/CSV analysis of phone timing and reviewed sampled pixel error.
- `03-source-code.zip`: use this for the six public Python programs. Read the package README before running a script.

Every ZIP includes a `README.md` that lists each file and its purpose.

## 2. Read reports and data

1. Extract the ZIP file.
2. Open `README.md` first.
3. Markdown (`.md`) files can be opened in VS Code, Typora, GitHub, or any text editor.
4. JSON and CSV files can be opened in VS Code, Python, Excel, LibreOffice, or another data tool.
5. Treat the English machine-translated editions as reading aids. Use the original Chinese record when exact wording matters.

## 3. Run lane detection without moving a vehicle

This is the recommended first code check. It processes an image, video, or ordinary camera and does not import the PWM vehicle driver.

```bash
mkdir lane-following-source
unzip 03-source-code.zip -d lane-following-source
cd lane-following-source
python3 -m venv .venv
source .venv/bin/activate
python -m pip install opencv-python numpy
python python/opencv_lane_detection.py --input /path/to/track-image.jpg --output lane-debug.jpg --no-display
```

For a video:

```bash
python python/opencv_lane_detection.py --input /path/to/run-video.mp4
```

For a USB or built-in camera:

```bash
python python/opencv_lane_detection.py --camera 0
```

The thresholds and assumed lane geometry were tuned for this project. A different camera, track, lighting condition, or image size normally requires recalibration.

## 4. Raspberry Pi hardware preparation

The vehicle-control program imports OpenCV, NumPy, Picamera2 and `Adafruit_PCA9685`. It expects a Raspberry Pi camera and a PCA9685 at I2C bus 1, address `0x40`.

A typical Raspberry Pi OS preparation is:

```bash
sudo apt update
sudo apt install -y python3-venv python3-opencv python3-numpy python3-picamera2 i2c-tools
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install Adafruit-PCA9685
sudo raspi-config
```

Enable I2C and the camera in `raspi-config`, reboot if requested, then confirm the controller address:

```bash
i2cdetect -y 1
```

Do not start with `opencv_drive_car.py`. That program initializes PWM and, after a three-second countdown, can request forward throttle when a lane target is detected. First test the camera and `opencv_lane_detection.py`; then verify steering centre, stop PWM, channel mapping and direction with the drive wheels raised. Use the hardware only under direct supervision and keep a physical way to disconnect power.

## 5. Preview the research website locally

Clone the full website repository, then serve it through HTTP. Opening `index.html` directly can block JSON loading in some browsers.

```bash
git clone https://github.com/Weibin1014/lane-following-research.git
cd lane-following-research
python3 -m http.server 8000
```

Open `http://localhost:8000` in a browser. Stop the server with `Ctrl+C`.

## 6. Publish a copy with GitHub Pages

1. Fork the repository or upload the downloaded repository to a new GitHub repository.
2. Open the repository's **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select the `main` branch and the `/ (root)` folder, then save.
5. Wait for the Pages workflow to finish. GitHub will show the public URL on the Pages settings screen.

When updating the site later:

```bash
git add .
git commit -m "Update research website"
git push origin main
```

## 7. Scope and limitations

- The public packages do not include the full thesis document.
- Phone timing is manual and the OpenCV/CNN sequence was not a matched randomized comparison.
- Pixel-error statistics describe measurable sampled frames, not physical lateral distance or every video frame.
- Run-specific thresholds and PWM values should not be copied to different hardware without calibration.
