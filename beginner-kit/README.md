# Beginner Setup Kit

This package accompanies the Lane / Lab research website. It takes a new user from a fresh Raspberry Pi OS SD card to a camera-only test and, only after manual checks, to the archived 16-second lane-following runner.

## Start here

1. Read `COMPLETE_SETUP_GUIDE.md` before connecting the motor battery.
2. Copy this folder to the Raspberry Pi.
3. Run `bash scripts/01_prepare_pi.sh`.
4. Reboot, then run `bash scripts/02_system_check.sh`.
5. Test the camera with `python scripts/03_camera_capture.py`.
6. Run the controller self-test and camera-only dry run from the guide.
7. Use the PWM scripts only with the car raised and the motor battery disconnected.

## Included programs

| File | Purpose | Can command PWM? |
| --- | --- | --- |
| `scripts/01_prepare_pi.sh` | Install Raspberry Pi system dependencies and create a Python environment | No |
| `scripts/02_system_check.sh` | Inspect the OS, camera, Python packages and I²C bus | No |
| `scripts/03_camera_capture.py` | Save one 160×120 camera image | No |
| `scripts/04_pca_neutral.py` | Set the project-specific stop and steering-centre values after explicit confirmation | Yes |
| `scripts/05_steering_calibrate.py` | Send one manually chosen steering value within the project range | Yes |
| `runner/v2_local_continuous_16s.py` | Archived bounded controller; camera-only unless `--drive` is supplied | Only with `--drive` |
| `runner/bounded_state_local_16s.py` | State and safety helper required by the runner | Indirect helper |
| `runner/s2_preview_core_local.py` | Vision core required by the runner | No |

## Project-specific reference values

- Camera: 160×120 at 20 Hz
- PCA9685: I²C bus 1, address `0x40`, 60 Hz
- Throttle channel: 0; stop/request: 370/400
- Steering channel: 1; left/centre/right: 440/365/290

These numbers describe the archived research car. They are requested PWM counts, not degrees, speed, or universal calibration values. Begin at the centre and calibrate every different car.

