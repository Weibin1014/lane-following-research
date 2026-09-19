# Independent sequence 11 frame rejection reason

Leave frozen candidates unchanged and use local state diagnostics on function return.

- 8 frames (129, 130, 169–172, 186, 310): The last independent valid observation is more than 0.15 seconds from the present; the actual age is about 0.188 to 0.330 seconds, and the timing assistance expires as designed.
- 3 frames (128, 137, 138): still within the validity period, the 15 white line sampling heights can be matched, but the maximum residuals relative to a single lateral displacement are 2.5, 2.5, and 3.0 pixels respectively, exceeding the 2 pixel limit. No yellow support check entered.

Therefore, this timing failure is not a current yellow support check failure. The main reasons are that the single-frame model cannot be continuously updated and the cross-frame geometric approximation is insufficient. A simple extension of 0.15 seconds or a simple relaxation of 2 pixels cannot be called a solution; these changes will turn this independent sequence into a parameter adjustment set.

Recommendations for the next stage: retain the current data and frozen conclusions, and use these two segments as development sequences; first establish a key frame artificial boundary reference, separate multiple connected areas of the yellow dotted line, and use visible marking line segments instead of line-by-line unique candidate fitting; the cross-frame relationship of the white line needs to consider different height changes caused by forwarding/turning, rather than a single horizontal displacement. Update status is supported by the current image, and expiration rules are kept independently. After the new candidate passes the development regression, the unseen sequences will be collected separately for evaluation without direct testing.

No real car code or frozen models have been changed in this round.
