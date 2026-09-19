> 2026-09-09 Revision and update at home: The abstract, literature review, summary, future work, appendices and acknowledgments have been added, the number of references has been verified to 12, and the real training curve and model parameter table have been added. For details, see [Document Verification and Revision Instructions](home_revision_2026-09-09/Document Verification and Revision Instructions.md). The following retains the previous record, in which the description of the vacancy in the above chapter has been superseded by this revision.

# Experiment progress and next step

Update date: 2026-09-09. Based on on-site feedback and archived reports of this task; this is the current progress entry, and the early "closed-loop not yet completed" records only represent the current status.

## Completed

- OpenCV has completed a real vehicle closed loop; on September 8, it completed three independent start-up full loop verifications.
- On September 9, the first batch of five CNN/OpenCV groups completed the pairing test and have been archived for verification. After completing the trial, the CNN touched the line an average of 3 times/circle, and OpenCV was 0; another CNN was retained for unfinished and debugging classification. The timing boundaries of the two logs are different, so no speed comparison will be made.
- Supplementary completion of OpenCV five times and then CNN five times on mobile phone. Each of the following times is confirmed by the operator to complete a circle, and both out-of-bounds and manual intervention are 0.

|Trials|OpenCV lap time (seconds)|CNN lap time (seconds)|OpenCV hit line|CNN hit line|
|---|---:|---:|---:|---:|
|1|11.24|16.23|0|1|
|2|11.91|16.64|0|2|
|3|13.30|16.20|0|3|
|4|13.63|18.00|0|2|
|5|13.60|18.23|0|1|
|Average|12.736|17.060|0|1.8|

- CNN resumes using the original model `models/mypilot.tflite`, WebSocket switches `local_angle`, CNN controls steering, fixed throttle 0.375 (current PWM mapping 400). The HTTP switching mode may not be maintained, and the model takeover cannot be determined based on the HTTP response; the debugging fault is no longer classified as the model cannot turn.
- The mobile timetable and research restrictions have been added to 5.2.4 and 6.2 of `Thesis_Main.docx`, and a backup before modification is retained.
- A short tutor email has been drafted: reporting progress and OpenCV debugging time, asking about the specific meaning of geometric evaluation and experiments that should be done as a priority. No confirmation sent or response received yet.

## Result bounds

- The two batches of experiments are reported independently and the average values ​​are not combined; the CNN hit line from 3 to 1.8 cannot be interpreted as model improvement.
- OpenCV uses the same battery five times, and the battery is replaced before starting CNN; the voltage or power is not measured, and OpenCV is fixed first and then CNN. The lap time difference cannot all be attributed to the algorithm, nor can it be asserted that the slowdown in later laps is caused by a drop in battery power.
- Mobile phone manual timing and on-site counting, small samples, and single tracks support descriptive comparisons under current conditions and do not represent positioning accuracy or long-term reliability.
- The first CNN supplementary test will be restored and verified first, and then it will be included in the official first test by the operator; keep this description. Completion table does not equal success rate for all attempts.
- The local mobile phone timing directory currently only has three JSON/Markdown summaries, and the original OpenCV supplementary test directory has not yet been verified for download. In the end, the CNN five-time client did not automatically save the sequential summary or frame log and cannot be repaired.

## Next step sequence

1. Confirm with the instructor whether the geometric evaluation refers to the center error of the image lane or the actual lateral deviation of the vehicle; whether the current completion status, line and circle collisions are sufficient, and if not, which item should be filled first.
2. While waiting for the reply, complete the original data backup, training records/model structure arrangement, real car and track data, and fill in Conclusion 6.1, Future Work 6.3, Summary and Appendix.
3. Decide whether to make up for geometric errors, processing delays of two methods with the same caliber, or lighting experiments according to the instructor's requirements; these have not yet been completed, and writing limitations cannot replace the clearly required core indicators. Currently there are no separate rerun arrangements due to battery factors.
4. Complete the references, unify the table of contents, figures, page numbers and list numbers, and check the complete manuscript.

Target: Form a complete draft that can be submitted to the instructor for review before September 12th (Saturday); whether new real vehicle experiments can be included depends on the instructor’s scope confirmation and collection progress, and will not be regarded as a final acceptance commitment.

## Related records

- [First batch of comparison verification] (CNN_OpenCV comparison verification_2026-09-09.md)
- [Mobile phone timing supplementary test](../experiment_data/2026-09-09/phone_timing/phone_comparison_report.md)
- [Remaining Supplementary List of Papers](Remaining Supplementary List of Papers_2026-09-09.md)
