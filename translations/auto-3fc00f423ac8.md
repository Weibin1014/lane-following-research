# Frame 222 quadratic fitting comparison

Candidates try quadratic curves only after local linear version rejection; at least 5 points, at least 10% height coverage, at most 2.5% height extrapolation, retaining 1.5 pixel residual and uncertainty bounds. Do not change the frozen version.

Frame 222: The maximum residual error of the straight line is 1.60 pixels; the quadratic curve is 0.85 pixels. The estimated near target is 71.53, PWM385, and the front and rear driving charts replay PWM390 and 388.

2391 saved pictures return: 2313 valid remain valid, 77 unavailable remain unavailable, only the frame is restored. This frame is involved in development, so all three sections are valid and do not constitute independent verification.

Leave-one-out check: Delete one sampling point one by one and refit. The PWM is 377, 386, 385, 384, 384, 386, 386, 385, 388; the range is 11, and the maximum prediction error of the left-out point is 2.50 pixels. It shows that the smaller training residual does not prove that the curve is reliable, especially the endpoints have a greater impact on the direction. Deploying a secondary fallback just to eliminate one frame rejection is currently not recommended.

Conclusion: The fixed independent results 319/320 of the local straight line candidates are retained; the secondary candidates are only used for experiments and the actual vehicle is not uploaded. Subsequent evaluation must focus on direction estimation sensitivity and measured bias, rather than optimizing output coverage to 100%.
