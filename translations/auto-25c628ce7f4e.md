# Keyframe visual comparison (rough reference, not true value)

All coordinates are based on the 160×120 original image, and the near target height is y=78. The following range is the approximate lane center range directly visually inspected, including the dotted line gap judgment error, and is not used to claim pixel accuracy, nor is it used for automatic parameter adjustment.

## Frame 128

![Original image](/Users/zhangweibin/Documents/Thesis/experiment_data/20260908_142524_316400/000128_raw.png)

A rough reference for near targets is x=58–72. The road is visible; the model has no near or far targets. The dashed yellow line has gaps, and the intervals are a rough visual estimate of the center of the lane.

## Frame 169

![Original picture](/Users/zhangweibin/Documents/Thesis/experiment_data/20260908_142524_316400/000169_raw.png)

A rough reference for near targets is x=60–74. The road is visible; the near target is directly matched to 66.75, which falls within the rough reference interval; the far target is missing, making it unusable.

## Frame 190

![Original image](/Users/zhangweibin/Documents/Thesis/experiment_data/20260908_142524_316400/000190_raw.png)

A rough reference for near targets is x=60–75. Effective frame comparison: near target 66.25, far target 64.25 (height 60%). Near targets fall within the rough reference interval.

## Frame 310

![Original image](/Users/zhangweibin/Documents/Thesis/experiment_data/20260908_142524_316400/000310_raw.png)

A rough reference for near targets is x=69–88. The path is visible; there is no goal. The posture of the picture is obviously different from that of the entrance, and it cannot be judged by the fixed lane width of the entrance.

## in conclusion

Examining the frames showed no visual evidence of having to stop for no track, but this does not prove that any interpolation scheme is reliable. Existing failures are at least partly a matter of far target availability, and all failures cannot be attributed to near-center mislocalization. Near/far targets need to be recorded and evaluated separately; hand-pushed images do not provide true corner or closed-loop trajectory errors.

Code review also found that the old pair_status=no_valid_path may be retained after the independent model is restored to ready. This field is only diagnostic metadata and does not affect the current ready determination, but it is easy to misread; the frozen version does not change, the next candidate should be explicitly marked independent_estimated and the original failure reason should be saved as a separate field.
