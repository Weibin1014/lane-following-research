# 8 seconds continuous section review

151128_545224: I/O exception occurred after 43 frames were valid, and the target in the last saved picture was still in the lane. Without a complete exception stack, the specific failed call cannot be located, nor can the parking write be proved to be successful. Users reported running off the track, which was a failed test.

151414_292040: 175/175 is valid, all paired; driving PWM360–406, visual maximum 33.54ms. 151551_148102: 175/175 valid, 173paired, 2independent_estimated; driving PWM353–401, visual maximum 38.71ms. Both time_limit and no exceptions were found, and users reported successful completion of the first and second half respectively. The target is randomly checked in the lane at the last frame. Completing a segment does not mean completing a continuous full circle.

Prepare an independent 12-second script, with the core and throttle unchanged at 400; Gate and watchdog share a 12-second constant, the outer period is 17 seconds, and the upper limit of snapshots is 220, which is enough under normal saving conditions of 0.1 seconds. Keep freshness, line loss lock, watchdog and physical power outage prompts. Passing the status self-test does not mean that the hardware will be able to stop when there is a communication failure.
