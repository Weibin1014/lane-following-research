# OpenCV development and experiment record: 7–8 September 2026

## Stage conclusion
The project progressed from offline vision and static camera checks to low-speed closed-loop driving. The same OpenCV version completed three separately started full-lap tests. Lap completion was confirmed by the operator; logs document output states, elapsed runtime and exceptions. These were not three uninterrupted laps. Ready-frame proportions are not detection accuracy.

## 7 September: offline and static vision
A replay of 600 numbered images (11400–11999) had no read failures. Continuous white boundaries were found in 580 frames; 3 were ambiguous and 17 had insufficient white evidence. At least one lane-centre candidate existed in 578 frames. Fixed-row targets were direct in 452 frames, interpolated in 7 and unavailable in 141. These are candidate and target counts, not accuracy scores.

The numbered sequence spanned 93865.008 seconds across recording sessions. Typical intervals had a median of 50 ms and 95th percentile of 52 ms, with 17 segmentation boundaries. The 141 unavailable records formed four time-contiguous segments of 40, 36, 36 and 29 records, each spanning approximately 1.55–1.95 seconds. Consecutive image numbers do not establish continuous driving.

The OV5647/Picamera2 camera captured 160×120 images at a configured 20 Hz. Static 30-second checks produced approximately 637–638 frames, about 21.23 frames/s. A floor-only scene produced 637 unavailable targets. These checks establish static operation and rejection of that particular scene, not general driving success.

## 8 September: control and vehicle tests
The runner added a five-fresh-frame start gate, loss-stop latch, freshness checks and a watchdog. Raised-wheel tests confirmed timed and target-unavailable stop behavior through operator feedback. Early straight runs drifted right; a fixed steering request of 365 supported the revised centre, followed by three short straight checks.

Boundary context and thin-line handling improved the first curve. Repeated failures at the second curve were retained. Three 15-second hand-pushed sequences contained 320, 319 and 320 frames; they are capture/replay evidence, not autonomous driving success. Local geometry then passed three 5-second second-curve runs, a check of the other curve, two 8-second route sections and a 12-second near-lap run before the three full-lap tests.

## Perception and control design
White/yellow HSV masks extract track boundaries in the lower image region. Boundary continuity, dark-road evidence, relative position and width constraints select lane geometry. Near targets use approximately 65% image height; farther evidence uses approximately 55% where available. Steering combines near lateral offset and a preview of road direction.

White thresholds were H 0–179, S 0–80, V 145–255; yellow thresholds were H 15–40, S 60–255, V 80–255. They are environment-specific settings.

Target sources are paired boundaries, independently estimated boundaries, and bounded local geometry. Interpolation between observed heights is distinct from reusing a previous frame. The final local approach does not rely on the explored temporal compensation to maintain readiness.

The PCA9685 uses address 0x40, I2C bus 1 and 60 Hz; throttle/steering channels are 0/1. Forward/stop requests are 400/370; steering centre is 365 with range 290–440. Increasing steering PWM corresponds to left turn after physical calibration. Frames must be fresh within 0.2 seconds; the software watchdog limit is approximately 0.25 seconds. Loss requests a latched stop. These are requested commands, not measured actuator feedback; an I/O failure can prevent a stop command reaching hardware.

## Replay validation and limitations
An independent-boundary version generated targets for 101 saved regression snapshots, which cannot represent all continuous frames. A temporal version reached 320/320 on the first hand-pushed sequence but only 308/319 on the second. Once used for development, that second sequence no longer counted as fresh holdout evidence.

Local fitting required at least three points, at least 5% image-height span, at most 5% image-height extrapolation (6 pixels), maximum residual 1.5 pixels, and bounded uncertainty and candidate disagreement. Development replay reached 320/320 and 319/319. A third independent sequence reached 319/320; frame 222 was rejected because its approximately 1.60-pixel residual exceeded 1.5. The rejection was retained.

Supply-related starting trouble and an Errno 5 incident were retained. Battery replacement restored starting, but voltage was not measured. Reconnecting interfaces was followed by successful runs, without proof that I/O faults were permanently eliminated.

## Three completed lap runs

| Run ID | Ready frames | Target sources | Steering PWM | Vision median / maximum |
|---|---|---|---|---|
| 20260908_152243_132290 | 344/344 | 343 paired + 1 independent | 354–405 | 28.27 / 42.38 ms |
| 20260908_152535_389653 | 345/345 | 343 paired + 2 independent | 356–408 | 28.08 / 39.47 ms |
| 20260908_152627_147979 | 345/345 | 343 paired + 2 independent | 354–408 | 27.87 / 37.69 ms |

All three enabled hardware output, ended at time_limit and recorded no error or watchdog_error. The operator confirmed completion. Together they contain 1034 frames: 1029 paired, 5 independent and no local-geometry targets. Thus these laps do not independently establish vehicle coverage of the local-geometry fallback. Three successful tests out of this final set do not establish the success rate of all development attempts or long-term reliability. The 16-second setting is a stop limit, not a measured lap time.

## Reproduction and next steps
Each run directory preserves the runner, core, state module, settings, frames.csv, summary and raw/debug images. Use the run-specific snapshots. The stage report and three_complete_laps_20260908 records contain integrity manifests. Further matched comparisons must align start position, success definition, speed/throttle conditions, battery state and repeat count; additional tracks, illumination, fallback coverage and I/O-independent stopping remain unverified.
