# 5-second left-turn exit to straightaway verification

Run: 20260908_133203_759340. The user confirms exiting the corner and successfully enters the straight. All 112 frames are ready and fresh, time_limit, no program/watchdog error.

Only the driving records when the throttle is requested at 400 are counted: PWM start 376, end 365, range 363–395; the last 10 records are 364, 366, 363, 363, 365, 368, 363, 365, 366, 365. Return to center occurs during the driving phase, not just stopping logic to force return to center. The normalized deviation of the near target ranges from 0.06875 to 0.003125; the median visual time consumption is 12.16ms.

In the first and last pictures, the target is between the yellow line and the right white line, and the next left bend can be seen ahead of the final section. The inspection results are consistent with user feedback; this is a partial turn-out verification and does not represent the completion of the other end of the left turn or the complete track.
