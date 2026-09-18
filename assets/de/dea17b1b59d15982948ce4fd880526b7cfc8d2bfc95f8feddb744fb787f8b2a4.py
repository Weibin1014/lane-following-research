"""Offline experiment only: horizontal white opening."""
import cv2
import numpy as np
import s2_preview_core_edge as base

def analyze(frame):
    original=base._SCOPE['build_color_masks']
    def masks(roi):
        _,yellow=original(roi)
        hsv=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        white=cv2.inRange(hsv,np.array([0,0,145]),np.array([179,80,255]))
        white=cv2.morphologyEx(white,cv2.MORPH_OPEN,np.ones((1,3),np.uint8))
        return white,yellow
    base._SCOPE['build_color_masks']=masks
    try:return base.analyze(frame)
    finally:base._SCOPE['build_color_masks']=original
