# The third candidate left bend failed frame diagnosis

Input: 20260908_124900_040821/000046_raw.png, 160×120. Replaying the candidate cores results in selected / insufficient_pairs / unavailable, which is consistent with the real vehicle log.

- y=66: The white road line of the original white mask is x=96..103; after the opening operation, x=101..103 is left. The current dark road inspection is based on the processed left edge. Only 2 of the 6 pixels on the left have V<145, the ratio is 1/3, and the 0.8 threshold has not been passed. This phenomenon still exists after supplementing the real image above the ROI.
- y=84: The original white mask is x=124..125 and 127..133, and the V=130 of x=126 in the middle is lower than 145, causing breakage. The opening operation removes the two-pixel segment, leaving 127..133. Check that the dark ratio of the 6 pixels on the left is 4/6, which fails the 0.8 threshold.
- Yellow line: There are no qualified yellow candidates for y=72, 90, 96, and 102; these cannot be called pure dotted line gaps. The original five-element strips have 23, 17, 4, and 5 yellow mask pixels respectively. After processing, they are still affected by morphology and segmentation support requirements.
- In the end, only y=78 and 108 had both white line and yellow candidates selected, and the required continuous pairing sequence could not be established.

Conclusion: ROI complementation context is not a sufficient repair. After morphological processing changes the left edge of the white line, and then checks the brightness of the original image based on the left edge, the white line itself or the broken white line may be included in the road surface, causing the real boundary to be rejected. The next candidate direction is to locate pavement inspection edges with original mask support, preserving continuity, bright ground exclusion, and parking requirements; not yet implemented, returned, or deployed.
