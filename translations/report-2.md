# Supplementary phone-timed comparison: 9 September 2026

Source: operator stopwatch timing and on-site observations. A lap was timed from starting to the vehicle front returning to the marked position. CNN original frame logs were not checked in this series.

| Trial order | OpenCV lap time (s) | CNN lap time (s) | OpenCV contacts | CNN contacts |
|---|---|---|---|---|
| 1 | 11.24 | 16.23 | 0 | 1 |
| 2 | 11.91 | 16.64 | 0 | 2 |
| 3 | 13.30 | 16.20 | 0 | 3 |
| 4 | 13.63 | 18.00 | 0 | 2 |
| 5 | 13.60 | 18.23 | 0 | 1 |

All five listed runs per method were confirmed to complete a lap, with zero departures and interventions. Mean times were 12.736 s for OpenCV and 17.060 s for CNN. Mean contacts were 0 and 1.8 per lap.

OpenCV was tested first, with the operator confirming one battery for its five runs. The battery was replaced before CNN; no subsequent replacement was reported. Battery and order effects prevent attributing the time difference entirely to the algorithm.

CNN trial 1 was initially planned as a recovery check and was subsequently designated trial 1 by the operator; this classification change is retained. Earlier HTTP mode-switch trouble and incomplete attempts are excluded from the completed-trial table. Five completed runs do not establish success across all attempts. Model-file contents were not re-compared in this series. CNN used WebSocket local_angle switching and fixed throttle 0.375; OpenCV requested throttle PWM 400.
