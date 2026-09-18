# Six-run pixel-offset evaluation: reviewed summary

Review and correction are complete for this evaluation. Initial annotation was AI-assisted, followed by the operator's visual review and feedback corrections. This is not independent double-blind annotation or exact manual ground truth.

Images are 160×120 pixels. Evaluation uses fixed row y=78 and image centre x=80; the midpoint of the horizontal centres of the left and right markings defines the lane centre. Of 60 sampled frames, 26 remain unmeasurable and 34 contribute to the calculations.

| Run | Measured / sampled | MSE (px²) | RMSE (px) | MAE (px) |
|---|---|---|---|---|
| CNN_03 | 6/10 | 370.46 | 19.25 | 14.67 |
| CNN_01R1 | 7/10 | 445.83 | 21.11 | 19.18 |
| CNN_02R1 | 5/10 | 218.89 | 14.79 | 12.15 |
| OpenCV_02 | 5/10 | 19.02 | 4.36 | 3.90 |
| OpenCV_03 | 6/10 | 13.83 | 3.72 | 2.58 |
| OpenCV_01R1 | 5/10 | 9.39 | 3.06 | 2.55 |

These results apply only to directly measurable sampled images, not all frames of a lap. Missing observations relate to dashed-marking gaps and endpoint visibility and cannot be assumed random. Missing frames are not filled with zero, replaced or selected by performance. Each run has only five to seven valid frames; no significance test was conducted. A single new-battery label does not imply constant voltage or actual speed. Recording duration is not an independent lap-time measurement.

Per-frame paths, coordinates and offsets remain in pixel_annotations_draft.csv. Review images and methods are in the detailed report. The draft filenames were retained for provenance; correction status is recorded by the review JSON files. Review means visual confirmation of displayed marks, without an independent quantitative estimate of marking-edge error.

The source summary's statement that the thesis had not yet been updated reflects its creation time. The current thesis draft now contains this evaluation; historical source files are retained unchanged.
