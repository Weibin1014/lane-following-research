# The second left bend: the local version was tested three times with real cars

All three times are 5 seconds, hardware output is enabled, 112/112 frames are ready and fresh, time_limit ends, and there is no program or watchdog exception. Users have reported that it bends normally. The total of 336 frames is the output validity statistics, not the accuracy.

|Run|Paired|Independent estimation|Local geometry estimation|Driving PWM range|Maximum adjacent PWM change|Median visual time consumption/maximum ms|
|---|---:|---:|---:|---|---:|---|
|20260908_145647_653443|112|0|0|387–406|7|26.02 / 37.22|
|20260908_150026_096366|111|1|0|364–402|8|26.35 / 39.70|
|20260908_150142_153103|108|4|0|365–402|7|25.62 / 40.33|

The output statistics are limited to requested_throttle=400 driving frames. Three times the core SHA256 is consistent: 95d59d65510ef4596948c277b16e3def86fe404a8aae71b4b4402715b7c1efa8.

Randomly check the middle and last frames of the first round and the last frames of the next two rounds. The target is between the yellow line and the white line on the right; the last frames of the last two rounds have entered the straight. Without manual annotation frame by frame, the positioning accuracy cannot be given. Three independent estimations totaling 5 frames did not trigger local geometry estimation. It cannot be claimed that this branch has completed the actual vehicle verification, nor can it be claimed that the full circle verification has been completed.

It is recommended to keep the code and throttle unchanged. The next step is to verify the 5-second performance of the same version in the left bend at the other end, and then arrange a longer continuous road section. Avoid mixing the successful results of previous thin versions as full circle evidence of the current version.
