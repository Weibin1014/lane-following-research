# The left-curved yellow candidate at the other end is missing

Input: 20260908_133717_324605/000069_raw.png, 160×120. The current core replays selected/consistent, but has no distant goal.

y=72: The original five-element band y=70..74 has no yellow threshold pixels, which is consistent with the performance of the dotted line gap.
y=66: The original complete five-element belt can obtain the yellow candidate x=41; the complete five-element belt can still obtain x=41 after full-image morphology. But the current ROI starts from y=66, and the five-line sampling is truncated to y=66..68. Yellow is at y=63..66, y=67 has only a single raw pixel (0 after processing), y=68 has none. Therefore, the conditions of supporting at least two rows per column and group width of at least 2 cannot be met. Candidates cannot be obtained even if the original mask is cropped directly to the ROI.

Only add 3, 4, and 6 rows of upper context for the yellow morphology, and then crop it back to the original ROI, which is still unavailable. Explain that the problem also includes sampling window truncation, and cannot only supplement the morphological context.

Next candidate direction: Complete yellow morphology and five-line sampling in the extended ROI, and clarify the full image/ROI coordinate conversion; the target height and two-line support conditions remain unchanged. Not implemented or deployed, historical negative sample regression is required.与先前白线开运算删除细白线的问题不同。
