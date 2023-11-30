import numpy as np
import cv2

def generate_mask(hsv_img, lower_bound, upper_bound):
    return cv2.inRange(hsv_img, np.array(lower_bound), np.array(upper_bound))
