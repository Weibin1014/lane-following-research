> 2026-09-09 Revision and update at home: The abstract, literature review, summary, future work, appendices and acknowledgments have been added, the number of references has been verified to 12, and the real training curve and model parameter table have been added. For details, see [Document Verification and Revision Instructions](home_revision_2026-09-09/Document Verification and Revision Instructions.md). The following retains the previous record, in which the description of the vacancy in the above chapter has been superseded by this revision.

# List of remaining supplements to the paper

For the latest progress, please see [Experimental Progress and Next Steps] (Experimental Progress_2026-09-09.md). The instructor's inquiry email has been drafted, but the sending and reply have not yet been confirmed; you can complete the backup and text while waiting. The goal is to form a review draft before September 12, and the scope of the new experiment is to be confirmed.

Verification objects: Thesis_Main.docx and Thesis work application.docx, combined with the two batches of experimental records on September 9, 2026. This checklist is a content check and not a certification of compliance with college formats or graduation requirements.

## Already added this time

- 5.2.4: List the mobile phone timing supplementary experiments and Table 5.5 separately. OpenCV averages 12.74 seconds and CNN averages 17.06 seconds; the average line collisions are 0 and 1.8 times/lap respectively.
- Retain the independent results of the original pairing experiment: CNN hits the line an average of 3 times, and the program time is 16.132 seconds. The two batches of data are not mixed, and the CNN model optimization is not claimed.
- 6.2: Clarify different batteries, unmeasured voltage and power, fixed grouping sequence, manual stopwatch error, small sample and single track, on-site observation, missing logs and software parking boundaries.
- Disclosed that the CNN first loop was first used for recovery verification and then included in the first classification process by the operator. Keep the HTTP mode switching issue and not treat all debug/failed runs as successes.
- Updated methods and discussion paragraphs to distinguish between the original 16-second runner and the supplementary 30-second runner.

## Prioritize the main text to be completed

1. 6.1 Summary of Work and 6.3 Future Work: currently only have titles. Summarize the corresponding relationship between the achieved content, main results and research objectives; future work includes controlling battery conditions, dual-method peer-to-peer recording, camera attitude and recovery data, and independent parking guarantee. It is not written as completed.
2. Abstract and keywords: There is no abstract in the current main file. Write an English abstract based on the final results; if other languages ​​and fixed formats are needed, check according to the college template.
3. Appendix A/B/C and Acknowledgments: Currently only the title. The appendix contains the final configuration, model version/hash, running script instructions, complete step-by-step records and fault classification; the author confirms the real help and title.
4. Literature review and citations: There are currently only 5 references, and many technologies reviewed lack corresponding citations. Supplement the relevant original literature around the actual adopted geometric control, behavioral cloning, distribution offset and embedded reasoning, and discuss the connection with this implementation; do not pile it up to make up the quantity.

## Evidence that can be supplemented by existing information

- Training process: The main text has 39 rounds and final loss, and adds training/validation loss curves, actual model structure/parameter table, verifiable batch size, learning rate, optimizer, loss function and checkpoint selection rules. Historical settings that cannot be restored are clearly unknown and cannot be directly passed off as the current default values.
- Track and platform: Add real car and track panorama, start and end/direction marks, known track size and lane width, exact Raspberry Pi model and software version. When dimensions are missing, they are measured or left unquantified and cannot be estimated from photos to true dimensions.
- Optimization process: Organize a short table of key OpenCV issues, corresponding modifications, and verification results, and retain failed solutions. Existing segmented tests can illustrate the development process, and coverage on different data cannot be used as a controlled optimization before and after comparison.
- Mobile phone trial archive: The local phone_timing directory currently only has result JSON and reports, and the downloaded mobile phone timing OpenCV original directory has not yet been found. Backup and corresponding verification should be completed. Subsequent CNN recovery clients did not automatically save each round summary/frame log, and known gaps remained disclosed.
- Formatting: finally unify figure numbering, in-text citations, table of contents, page numbers, independent list numbering, and chapter pagination. The current numbered list has the phenomenon of cross-chapter continuation. The summary and complete conclusion should be added before final typesetting.

## The research scope that most needs to be confirmed with the supervisor

The application mentions "a geometric method... used as the metric" and plans to evaluate lane-center deviation, latency, trajectory stability and changing lighting conditions. The current text mainly evaluates line collision, full lap completion and timing. There is no lateral positioning error supported by manual annotation or independent reference, and there is no equivalent delay and controlled robustness test between the two methods.

To be clear: is the geometric method the OpenCV controller in this paper, or must it be used as an additional evaluation indicator. If a geometric error indicator must be provided, simply writing limitations cannot replace the result; it can be evaluated whether the existing image is suitable for manual annotation of the image space center error, but the CNN supplementary test lacks corresponding frame data, and the image pixel error is not equal to the centimeter-level trajectory error. If the current system-level descriptive comparison is acceptable to the instructor, the scope of the study will be explicitly adjusted to include unfinished measurements in limitations and future work.

At this stage, there will be no separate rerun arrangements due to battery factors. Whether to perform geometric evaluation, peer delay or robustness testing depends on the final confirmed core research objectives.
