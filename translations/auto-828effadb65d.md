# Near positioning and direction separation experiment

Both sections are now development sequences; the frozen version has not been changed.

1. Add 57.5% to the original 55% and 60% of the far target: single frame coverage remains unchanged.
2. Add 62.5%: the second single frame is 269→282, and the first segment is 312 unchanged. However, the distance between near and far is only 3 pixels, and the original direction formula is sensitive to pixel noise, so this candidate is not deployed.
3. Local direction fitting: Fit the slope only when there are at least 4 reliable center points, the span is ≥7.5%, and 65% of the close targets are available; the maximum residual error is ≤1.5 pixels, and the slope uncertainty including the 0.5 pixel noise lower limit corresponds to PWM ≤ 8. Output flag direction_estimated, do not fake distant targets. Thresholds represent experimental conditions and are not calibration guarantees.

The second section of the direction fitting single frame is 269 → 285, and the first section 312 is maintained. After combining with the original 0.15 second timing assist, the first segment is 320/320, and the second segment is 311/319 (the original frozen version is 308/319). Remaining failures 128–130, 170–172, 186, 310. It is still not passed stably and the driving script is not generated.

The next focus is still whether the current frame can form reliable central evidence; simply adding a closer distant target, increasing model complexity, or extending the historical validity period are not proven solutions. The complete negative sample regression and Raspberry Pi latency verification has not yet been completed.
