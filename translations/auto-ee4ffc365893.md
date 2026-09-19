# 2026-09-12 Pixel deviation evaluation: first draft of AI-assisted annotation

## state

The 990 original images and 1496 records of the six selected experiments have been backed up; see six_run_audit.json for the exact number. This report only evaluates 10 pictures that are evenly selected according to time in advance, for a total of 60 pictures. 34 pictures can be measured directly, and 26 pictures cannot be measured directly. The statistical values ​​are the first draft of AI-assisted annotation, which has not been independently reviewed by the operator. It is not a true value of manual annotation, nor is it a complete error of the entire circle.

The main paper file has not been modified. Other trials will not be included in this statistics according to user requirements, and the original backup will be retained.

## Unified rules

- The original image is 160×120; the zero starting coordinate is fixed at y=78 (line 79 of the array), and the image center is x=80 according to the existing convention. This rule is determined by this discussion and does not claim that the instructor explicitly specified this line. According to strict discrete pixel geometric center, it should be 79.5; the 80 confirmed by the user is used here, which is consistent six times.
- The left boundary position is defined as the lateral center of the yellow lane separation marking line on the line, and the right boundary is the lateral center of the right white marking line. The center of the marking line is used instead of the inner edge of the marking line. Lane center=(left_x+right_x)/2; e=lane center−80; MSE=mean(e²), RMSE=sqrt(MSE), MAE=mean(|e|). MSE unit is px², others are px.
- Extract frames according to 10 equally spaced target moments within each available recording time range, and select the nearest original image. OpenCV only selects from the saved frames of throttle request 400; the saved records of CNN selected runs are local_angle, user throttle 0.375. The use of time index is not track position alignment, and the same serial number cannot be called the same physical location.
- Do not replace images based on the size of the deviation, do not read OpenCV near_offset, near_x or identify red dots as true values ​​for evaluation.
- If there is a yellow dotted gap or unclear endpoint at the fixed line, it is marked as unable to be measured directly. No interpolation, extrapolation, carry over from previous frame, zero padding, or sample replacement. The out-of-bounds incident was retained as it was, and the entire test was not eliminated due to driving performance.

## Mark source and reviewability

This is AI-assisted visual annotation, not manual annotation done by a user or instructor. The assistant views all 60 original image thumbnails and fixed rows of 5x nearest neighbor magnification strips one by one, gives an estimate of the abscissa of the white marking line, and selects a local range near the yellow marking line. For samples where the yellow marking line can be directly measured, the color contrast of min(R,G)-B is used to extract the marking line in line 78 of this range: threshold = max (40, local maximum contrast × 0.6), and the midpoint of the first and last pixels passing the threshold is taken. This independent auxiliary rule applies two methods at the same time, which is different from the HSV controller of vehicle operation, but there will still be color and threshold errors and cannot be called unbiased artificial truth. The white line coordinates are visual estimates, and the annotator error is not quantified. The six review pictures have been viewed by the assistant and still need to be independently reviewed by the operator.

In the picture, the blue vertical line is x=80, the gray horizontal line is y=78, the orange point is the center of the yellow marking line, the green point is the center of the white marking line, and the red point is the midpoint of the two. Note that these are the marks for this evaluation and have different meanings from the colors on the original identification map of the vehicle.

## Preliminary step-by-step results

|Trials|Measurable/sampled|Unmeasured|MSE(px²)|RMSE(px)|MAE(px)|
|---|---:|---:|---:|---:|---:|
|CNN_03|6/10|4|370.5|19.2|14.7|
|CNN_01R1|7/10|3|445.8|21.1|19.2|
|CNN_02R1|5/10|5|218.9|14.8|12.2|
|OpenCV_02|5/10|5|19.0|4.4|3.9|
|OpenCV_03|6/10|4|9.0|3.0|2.3|
|OpenCV_01R1|5/10|5|5.8|2.4|2.0|

In this batch of directly measurable samples, OpenCV's first draft RMSE is smaller. No conclusions can be drawn on significance, full-turn accuracy, centimeter deviation, long-term reliability or speed advantages. There are 26/60 unmeasured frames in total. The missing frames are related to the position of the dotted line and the vehicle attitude, and are not necessarily random. The number of samples actually involved in the calculation of the two methods is also different. These statistics only hold true for measurable samples. There are only 5–7 valid images at a time, and consecutive frames are not independent experiments.

![Sequential first draft RMSE](rmse_draft.png)

![Measurement examples](measurement_examples_draft.png)

## All sample review pictures

- [CNN_03: All 10 pictures, including untestable samples](CNN_03_annotated_review.png)
- [CNN_01R1: All 10 pictures, including untestable samples](CNN_01R1_annotated_review.png)
- [CNN_02R1: All 10 pictures, including untestable samples](CNN_02R1_annotated_review.png)
- [OpenCV_02: All 10 pictures, including untestable samples](OpenCV_02_annotated_review.png)
- [OpenCV_03: All 10 pictures, including untestable samples](OpenCV_03_annotated_review.png)
- [OpenCV_01R1: All 10 pictures, including untestable samples](OpenCV_01R1_annotated_review.png)

## Follow-up

1. Check the position of the white/yellow marking line and the unmeasured mark on the above overlay; keep the modification basis in pixel_annotations_draft.csv. The verification status must be clearly marked before official statistics.
2. The 26 unmeasured frames are reserved as missing. If adjacent row interpolation is used to supplement, unified rules need to be defined and verified separately, and the direct measurement results cannot be quietly changed.
3. Formal papers should report sampling rules, valid/missing numbers, pixel coordinate conventions, annotation sources and limitations. This first draft is not currently automatically written to Thesis_Main.docx.

The calculation and frame drawing scripts are under experiments/pixel_evaluation_20260912, and the entire original image path can be traced in pixel_annotations_draft.csv. sha256.json is a verification list of local backup files. It does not mean that the hash has been compared with the Raspberry Pi file by file.

## Manual review and correction records

- CNN_01R1: assistant corrected following user feedback; corrected point not yet reconfirmed by user; see [CNN_01R1_sample6_review.json](CNN_01R1_sample6_review.json) for details.
- CNN_02R1: user confirmed all three corrected green markers acceptable; see [CNN_02R1_review_corrections.json](CNN_02R1_review_corrections.json) for details.
- CNN_03: user confirmed revised displayed markers acceptable; see [CNN_03_review_corrections.json](CNN_03_review_corrections.json) for details.
- OpenCV_02: corrected points pending user confirmation; see [OpenCV_02_review_corrections.json](OpenCV_02_review_corrections.json) for details.
