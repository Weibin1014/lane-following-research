# The full window version fails to bend left at the other end

Running 20260908_134855_688477, frame 69 replays selected / insufficient_pairs / unavailable, consistent with the log.

There are candidates for the white line and yellow in this frame at y=102, 96, 72, and 66; there are no yellow candidates at y=90, 84, and 78. The near group 102/96 and the far group 72/66 are separated by 4 sampling steps, which exceeds the 3 allowed for consecutive pairings. Therefore, each of the two groups has only 2 nodes and cannot form a continuous path with at least 3 nodes. It's not that the yellow window in the distance is still truncated, nor that there are only two candidates overall.

The existing output has no near targets; even if only the cross-band connection is relaxed, the y=78 near target still needs to be interpolated between y=72 and 96, and the span of 0.20 exceeds the upper limit of the target function of 0.15. Therefore, changing only one interval threshold cannot completely solve the problem, and two items cannot be relaxed at the same time without verification.

The last frame of the log requested stop 370/return 365, no I/O error. The current full window fix is ​​not equivalent to eliminating the sparse pairing caused by the yellow dotted line. The next step is to check the feasibility of the original yellow information and denser sampling near y=78 offline, and then determine the model plan; the deployment version will not be automatically changed.
