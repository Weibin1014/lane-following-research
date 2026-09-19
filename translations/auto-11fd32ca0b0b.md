#Competition path verification candidates (offline)

Based on encrypted sampling. There are up to 64 scoring close paths; first make the existing yellow and white continuous matching, and then compare the effective path center. No valid paths, overlimits, or central differences are still rejected; similar paths are merged into the same explanation. Target interpolation, color and parking conditions are preserved. Currently, the detection is repeated once, and the performance still needs to be measured on the Raspberry Pi.

1328 pictures are returned: 1244 remain ready, 77 remain unavailable, and 7 are restored to ready; 29 non-track surfaces are still unavailable. The two new encryption failures of the first candidate have been recovered, and the other one has recovered PWM395 at frame 69 this time. The original effective output changes by 115 frames, and the maximum PWM difference is 3. These are not accuracy rates or real-car verification results.

The control branch test passes: candidate over-limit rejection, two valid paths with different positions are rejected, no valid path is rejected, and equivalent paths are accepted. The median time spent on replaying the 30 failed frames on Mac was 1.26ms, which does not mean the time spent on the Raspberry Pi. Not deployed.
