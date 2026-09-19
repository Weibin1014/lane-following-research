# Local geometry candidate: third stage fixed version verification

20260908_144230_773780, 320 frames. Before verification, the core SHA256 was consistent with the frozen record, and the parameters were not adjusted this time.

319/320 are valid, the only failure is frame 222. Effective sources: 227 frames of pairing, 41 frames of independent estimation, 51 frames of local geometry estimation. Full sequence PWM363–399; maximum change between adjacent valid frames is 9. Maximum near target extrapolation is 5% of image height (6 pixels). No timing information is used.

The track is visible in frame 222; the near target 72 exists, but the far target is missing. The maximum residual of the local 9 center candidate fittings is 1.60 pixels, which exceeds the freezing 1.50 pixel threshold and is rejected. The threshold was not therefore changed to 1.60. The independent verification results of this sequence are retained and cannot be overwritten by modified reruns.

Conclusion: Independent sequence results are more promising than the previous timing candidate, but different acquisition sequences cannot be directly compared strictly for effectiveness. Under the current strict failure-to-stop control rules, it is still possible to stop at this frame; it does not pass the non-failure standard throughout the entire process. No driving arrangements yet. There is no need to continue collecting. This time, the fitting model error/geometric curvature and measurement uncertainty should be analyzed first to avoid adjusting parameters based on threshold values ​​alone.
