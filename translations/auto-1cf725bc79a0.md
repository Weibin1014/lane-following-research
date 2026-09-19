# Fixed candidate independent sequence verification: failed

New sequence 20260908_142524_316400, 319 frames. Before verification, check the hashes of temporal_probe.py and s2_preview_core_independent.py, which are consistent with the frozen version; no parameters were adjusted in this round.

Results: 240 frames paired, 29 frames independently estimated, 39 frames timing estimated, 11 frames unavailable, that is, 308/319 valid (96.55% output coverage, not accuracy). The failure intervals are 128–130, 137–138, 169–172, 186, and 310, with a maximum length of 4 frames. The maximum PWM change between effective adjacent frames is 14. Compared with development sequence 320/320, this candidate does not yet have stable passing evidence.

Checking the original pictures of 128, 169, and 310, the track is still visible, and the failure cannot be directly attributed to leaving the track. Positions such as 169–172 have previously had 3 consecutive frame timing estimates, and further analysis of the historical validity period and geometric constraints is required; the validity period cannot be directly extended to cover up the lack.

Conclusion: Keep the independent evaluation results, do not deploy driving, and do not require users to continue test runs. The current data can be converted into the next stage of development data, but after modification, new data needs to be obtained for independent verification, and this time cannot be reused as evidence of unbiased passing. Save the stage results first, and the next round requires structural improvements/artificial boundary truth values ​​and model evaluations, rather than continuing to extend historical information or relax protection.
