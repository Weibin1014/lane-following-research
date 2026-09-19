#!/usr/bin/env python3
"""Send the archived car's stop and steering-centre PWM values once."""

import argparse

ADDRESS = 0x40
FREQUENCY_HZ = 60
THROTTLE_CHANNEL = 0
STEERING_CHANNEL = 1
THROTTLE_STOP = 370
STEERING_CENTRE = 365


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-disconnected",
        action="store_true",
        help="Confirm motor battery is disconnected and the car is raised.",
    )
    args = parser.parse_args()
    if not args.confirm_disconnected:
        parser.error("disconnect the motor battery, raise the car, then add --confirm-disconnected")

    import Adafruit_PCA9685

    print("Using archived project values; these may be wrong for different hardware.")
    pwm = Adafruit_PCA9685.PCA9685(address=ADDRESS, busnum=1)
    pwm.set_pwm_freq(FREQUENCY_HZ)
    pwm.set_pwm(THROTTLE_CHANNEL, 0, THROTTLE_STOP)
    pwm.set_pwm(STEERING_CHANNEL, 0, STEERING_CENTRE)
    print(f"Throttle channel {THROTTLE_CHANNEL} -> {THROTTLE_STOP} (project stop request)")
    print(f"Steering channel {STEERING_CHANNEL} -> {STEERING_CENTRE} (project centre request)")
    print("Disconnect servo/ESC power immediately if the hardware moves unexpectedly.")


if __name__ == "__main__":
    main()
