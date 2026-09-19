#!/usr/bin/env python3
"""Send one manually chosen steering PWM value; there is no automatic sweep."""

import argparse

ADDRESS = 0x40
FREQUENCY_HZ = 60
THROTTLE_CHANNEL = 0
STEERING_CHANNEL = 1
THROTTLE_STOP = 370
MIN_PROJECT_VALUE = 290
MAX_PROJECT_VALUE = 440


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("value", type=int, help="Start at 365, then change in steps of 5")
    parser.add_argument(
        "--confirm-disconnected",
        action="store_true",
        help="Confirm motor battery is disconnected and the car is raised.",
    )
    args = parser.parse_args()
    if not args.confirm_disconnected:
        parser.error("disconnect the motor battery, raise the car, then add --confirm-disconnected")
    if not MIN_PROJECT_VALUE <= args.value <= MAX_PROJECT_VALUE:
        parser.error(f"value must remain within {MIN_PROJECT_VALUE}..{MAX_PROJECT_VALUE}")

    import Adafruit_PCA9685

    pwm = Adafruit_PCA9685.PCA9685(address=ADDRESS, busnum=1)
    pwm.set_pwm_freq(FREQUENCY_HZ)
    pwm.set_pwm(THROTTLE_CHANNEL, 0, THROTTLE_STOP)
    pwm.set_pwm(STEERING_CHANNEL, 0, args.value)
    print(f"Steering channel {STEERING_CHANNEL} -> {args.value}")
    print("Observe the wheels. Never force the servo against a mechanical stop.")
    print("Use Ctrl+C or disconnect servo power if anything is unexpected.")


if __name__ == "__main__":
    main()
