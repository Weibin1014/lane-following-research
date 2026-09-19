# Complete yellow sampling window candidate

Expand the top edge of the processing ROI upward by 6 pixels, keeping the original 55% to 90% sampling height unchanged. 6 pixels are used for the upper 2 rows of five rows of samples and the context of the yellow opening and closing operations. Synchronously adjust the coordinate origin of detection, pairing and original white edge reference; original white context processing is retained. Two-row support, pairing continuity, and control requirements have not been reduced. The processing ROI is also used for white, so it cannot be said to only affect yellow.

1253 original 160×120 images are returned: 1167 remain ready, 83 remain unavailable, and 3 are restored to ready. All 29 known ground pictures without track remain unavailable. The PWM of 464 original valid pictures has changed, with a maximum of 9.

This failed frame 20260908_133717_324605/000069_raw.png restores far target x=70, near target x=81, and PWM394. The two historical recovery frames 000481 and 000493 are track images. The original image and output center coordinates have been viewed, and no artificial frame-by-frame true values ​​have been established.

The numbers include repeated static frames and JPEGs. They are only regression statistics on the saved pictures and do not represent accuracy or actual vehicle control success rate. The candidate has not yet been deployed or statically verified. The next step is independent static verification, first fixing known loose connections without automatically running the motor.
