# Complete Beginner Setup Guide

This guide starts with a blank microSD card and ends with a staged, bounded test of the archived lane-following controller. Copy one command block at a time and read the expected result before continuing.

> **Hardware safety:** keep the drive-motor battery disconnected through Steps 1–12. Raise the car so no driven wheel touches the floor before any PWM check. Keep the main power switch or battery connector within reach.

## Project profile

- 1:16 scale research car
- Raspberry Pi with an OV5647 CSI camera
- PCA9685 on I²C bus 1, address `0x40`, 60 Hz
- Camera configuration: 160×120, 20 Hz
- Archived channel map: throttle 0, steering 1
- Archived PWM requests: throttle stop/forward 370/400; steering left/centre/right 440/365/290

The PWM numbers are specific to the research car. They are controller counts, not degrees or measured speed.

## 1. Prepare the parts

- Raspberry Pi supported by current 64-bit Raspberry Pi OS
- Suitable Raspberry Pi power supply
- microSD card and card reader
- Compatible CSI ribbon cable and OV5647 camera
- PCA9685 board
- steering servo, ESC/motor system and the car chassis
- a separate regulated 5–6 V servo supply when required by the servo/PCA9685 setup
- jumper wires, standoffs and a physical power disconnect

Do not assemble or rewire powered electronics.

## 2. Flash Raspberry Pi OS

1. Install Raspberry Pi Imager on the computer that has the SD-card reader.
2. Choose a compatible Raspberry Pi device.
3. Choose the current 64-bit Raspberry Pi OS recommended for that device.
4. Choose the microSD card.
5. In OS customisation, set a hostname, username, password, Wi-Fi country/network, timezone and enable SSH with password authentication.
6. Write the card, wait for verification, then eject it.

Record the username and hostname. The examples below use `student` and `lane-car`; replace them with your choices.

## 3. First boot and SSH

Insert the card, leave the motor battery disconnected, power the Raspberry Pi, and allow several minutes for first boot. From another computer:

```bash
ssh student@lane-car.local
```

If `.local` discovery fails, find the Pi's address in the router and use:

```bash
ssh student@192.168.1.123
```

Update the operating system:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Reconnect by SSH after the reboot.

## 4. Shut down before assembly

```bash
sudo shutdown -h now
```

Wait until activity stops, remove Raspberry Pi power, and keep all vehicle power disconnected.

## 5. Assemble the car and camera

1. Build the chassis and steering linkage according to the chassis manufacturer.
2. Mount the Raspberry Pi on standoffs where wires cannot enter the drivetrain.
3. Mount the camera facing forward. Keep the horizon level and leave the lens unobstructed.
4. Open the CSI connector latch, insert the correct ribbon in the documented orientation, close the latch, and avoid sharp ribbon bends.
5. Raise the car on a stable stand so the driven wheels and steering can move freely.

## 6. Wire the PCA9685

The research mapping is:

| Raspberry Pi | Physical pin | PCA9685 logic pin |
| --- | ---: | --- |
| 3.3 V | 1 | VCC |
| SDA / GPIO 2 | 3 | SDA |
| SCL / GPIO 3 | 5 | SCL |
| Ground | 6 | GND |

Connect the steering servo signal to PCA9685 channel 1 and the ESC signal to channel 0 for this archived project. Supply servo rail `V+` from a suitable separate 5–6 V supply and connect grounds in common. Do not use the Pi's 5 V pin as a general servo power source.

Verify every wire against the labels printed on the actual board before applying power.

## 7. Download the setup kit

On the Raspberry Pi:

```bash
cd ~
git clone https://github.com/Weibin1014/lane-following-research.git
cd lane-following-research/beginner-kit
```

Or download `04-beginner-setup-kit.zip`, copy it to the Pi, then run:

```bash
mkdir -p ~/lane-following-beginner
unzip 04-beginner-setup-kit.zip -d ~/lane-following-beginner
cd ~/lane-following-beginner
```

## 8. Install the software

```bash
bash scripts/01_prepare_pi.sh
```

Enable I²C:

```bash
sudo raspi-config
```

Choose **Interface Options → I2C → Yes**, exit, then reboot:

```bash
sudo reboot
```

Current Raspberry Pi OS uses the `rpicam-*` camera stack; a separate legacy camera toggle is not required.

## 9. Run the read-only system check

Reconnect, return to the kit and run:

```bash
cd ~/lane-following-research/beginner-kit
bash scripts/02_system_check.sh
```

Expected checks:

- `cv2`, `numpy`, `picamera2` and `Adafruit_PCA9685` show `PASS`.
- The camera inventory lists a camera.
- The I²C table contains `40` when the PCA9685 is powered and wired correctly.

The script scans devices but does not initialise PWM.

## 10. Test the camera without PWM

First use the Raspberry Pi camera utility:

```bash
rpicam-hello --timeout 5000
```

In a headless SSH session, list cameras instead:

```bash
rpicam-hello --list-cameras
```

Capture the same small resolution used by the project:

```bash
~/lane-env/bin/python scripts/03_camera_capture.py
```

Copy the JPEG to another computer if needed:

```bash
scp student@lane-car.local:~/lane-following-research/beginner-kit/camera-tests/*.jpg .
```

Check that the track is visible, centred, sharp and not heavily tilted before continuing.

## 11. Verify the archived controller files

```bash
cd ~/lane-following-research/beginner-kit/runner
sha256sum s2_preview_core_local.py
```

Expected SHA-256:

```text
95d59d65510ef4596948c277b16e3def86fe404a8aae71b4b4402715b7c1efa8
```

Run the internal safety-state tests:

```bash
~/lane-env/bin/python v2_local_continuous_16s.py --self-test
```

Do not continue if a self-test fails.

## 12. Run the camera-only controller

Place the raised car in its normal track-centred pose. Keep the motor battery disconnected. Run without `--drive`:

```bash
~/lane-env/bin/python v2_local_continuous_16s.py
```

The default branch captures and evaluates camera frames without importing the PCA9685 driver. Review its output and saved raw/debug images. Continue only when frames are fresh and the lane target is consistently ready. If `ready_frames` is zero, inspect camera position and saved images before changing thresholds.

## 13. Request neutral PWM

This is the first PWM-producing step. Confirm all of the following:

- drive-motor battery disconnected
- car raised securely
- correct channel wiring
- physical power disconnect within reach

Then run:

```bash
cd ~/lane-following-research/beginner-kit
~/lane-env/bin/python scripts/04_pca_neutral.py --confirm-disconnected
```

Disconnect servo/ESC power immediately if anything moves unexpectedly.

## 14. Calibrate steering manually

Start at the archived centre and move in small increments. Each command sends one value; the script never sweeps automatically.

```bash
~/lane-env/bin/python scripts/05_steering_calibrate.py 365 --confirm-disconnected
~/lane-env/bin/python scripts/05_steering_calibrate.py 360 --confirm-disconnected
~/lane-env/bin/python scripts/05_steering_calibrate.py 370 --confirm-disconnected
```

Find the true mechanical centre for the assembled car. Approach left and right limits slowly and stop before the linkage strains. Record the calibrated centre, direction and usable endpoints. Do not assume that 290/365/440 fits another servo or linkage.

## 15. First bounded drive test

Before motion, repeat the self-test and camera-only run. Clear the track, keep the car under direct supervision, and prepare to disconnect power. The archived runner enables PWM only when `--drive` is supplied:

```bash
cd ~/lane-following-research/beginner-kit/runner
~/lane-env/bin/python v2_local_continuous_16s.py --self-test
~/lane-env/bin/python v2_local_continuous_16s.py
~/lane-env/bin/python v2_local_continuous_16s.py --drive
```

Read and answer the runner's confirmations at the terminal. Its archived controls include a five-frame readiness gate, lane-loss stop latch, stale-frame and watchdog checks, and a 16-second time limit. These controls reduce risk but do not replace direct supervision or hardware calibration.

## 16. Optional CNN/DonkeyCar path

The archived CNN work used DonkeyCar 5.3.0, TensorFlow Lite Runtime 2.14.0 and `mypilot.tflite`. A fresh installation of current DonkeyCar may differ from that environment, so recreate it as a separate compatibility task rather than overwriting the tested OpenCV environment. The archived command was:

```bash
cd /home/student/projects/mycar
python manage.py drive --model models/mypilot.tflite --type tflite_linear
```

The working control mode was `local_angle`: model steering with fixed throttle 0.375. This documents the research setup; it is not a validated clean-install recipe for every Raspberry Pi release.

## 17. Stop and shut down

1. Stop the program with `Ctrl+C`.
2. Disconnect drive-motor battery and servo power.
3. Shut down the Pi:

```bash
sudo shutdown -h now
```

4. Wait for SSH to disconnect and activity to stop before unplugging Raspberry Pi power.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| SSH hostname is not found | Confirm Wi-Fi settings, check the router, then connect by IP address. |
| No camera listed | Power down and reseat the CSI ribbon; verify the connector and cable orientation for the Pi model. |
| `rpicam-hello` missing | Run the preparation script and confirm Raspberry Pi OS packages are current. |
| No `40` in `i2cdetect` | Enable I²C, check VCC/GND/SDA/SCL and board power; do not run PWM scripts. |
| Python import fails | Activate/use `~/lane-env` and rerun `01_prepare_pi.sh`. |
| `ready_frames: 0` | Inspect the saved raw/debug frame and normal driving pose before threshold changes. |
| Steering direction reversed | Stop power and correct the verified software mapping or servo configuration before driving. |
| Servo chatters or strains | Disconnect servo power immediately; inspect supply, ground, linkage and calibration range. |
| Motor reacts at the stop value | Disconnect the battery immediately and calibrate the ESC; 370 is only the archived car's request. |

## Official references

- Raspberry Pi getting started: https://www.raspberrypi.com/documentation/computers/getting-started.html
- Raspberry Pi configuration and I²C: https://www.raspberrypi.com/documentation/computers/configuration.html
- Raspberry Pi camera software: https://www.raspberrypi.com/documentation/computers/camera_software.html
- Adafruit PCA9685 wiring: https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/hooking-it-up
- DonkeyCar Raspberry Pi setup: https://docs.donkeycar.com/guide/robot_sbc/setup_raspberry_pi/
- DonkeyCar calibration: https://docs.donkeycar.com/guide/calibrate/
- GitHub Pages publishing: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Preview or republish the research website

On an ordinary computer with Git and Python:

```bash
git clone https://github.com/Weibin1014/lane-following-research.git
cd lane-following-research
python3 -m http.server 8000
```

Open `http://localhost:8000` and stop the server with `Ctrl+C`. To publish a fork, open the repository's **Settings → Pages**, select **Deploy from a branch**, then select `main` and `/ (root)`.
