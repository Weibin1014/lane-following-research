# 2026-09-08: Thin white line version 5 seconds left bend repeated verification

Conclusion: All three times ended within the time limit, and the user confirmed that the entire process followed the curve; it was verified through short-term repeated verification under the current starting point, speed and scene.

Solution: OpenCV yellow and white line candidates and continuous pairing, near and far target preview; white mask uses 1×3 horizontal opening operation to retain the real context above the ROI and the original white edge reference check. Servo midpoint 365, range 290–440, forward throttle 400, stop 370; maximum 5 seconds, target loss/image expiration, early stop.

|Running Directory|Effective/Total Frames|Driving PWM|Median Visual Time Elapsed Time (ms)|Stop Reason|
|---|---|---|---|---|
|20260908_131031_179493|112/112|385–401|11.91|time_limit|
|20260908_131328_122874|112/112|383–401|11.56|time_limit|
|20260908_131416_561369|112/112|383–400|11.55|time_limit|

A total of 336 frames, all fresh and ready, no program or watchdog error reported. The three runner, gate and visual core snapshot hashes are consistent. PWM and time-consuming statistics only take the driving record of requesting accelerator 400; PWM is the requested value, not the actual measurement of the hardware. The targets in the last frame examined are all between the yellow line and the right white line, and the near targets are close to the center of the image.

Range limitations: Effective frame ratio is not accuracy; triple dash is not full lap or multi-environment validation. Replaying the same image from the old version is also valid, but improvements in the new version cannot be quantified based on this. Slight sliding after parking has been reported by users; stopping PWM does not equate to a physical instantaneous stop. The root cause of the initial I/O failure has not yet been determined.

Fixed this version to end this round of repeat sports cars. Follow-up arrangements include the latest core straight line regression, complete track segment verification, and comparison of CNN/OpenCV under the same conditions; these have not yet been completed.
