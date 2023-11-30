import numpy as np
import cv2

class MaskGenerator:
    def __init__(self):
        pass
      
    def ball_generate_mask(hsv_img):
        # 424 version
        lower = np.array([0, 20, 187])
        upper = np.array([37, 255, 255])
        lower1 = np.array([118, 0, 0])
        upper1 = np.array([255, 255, 255])
        
        mask1 = cv2.inRange(hsv_img, lower, upper)
        mask2 = cv2.inRange(hsv_img, lower1, upper1)

        mask = mask1+mask2
        
        return mask

    def flag_generate_mask(hsv_frame):
        # 424 version
        low_yellow = np.array([0, 56, 169])
        high_yellow = np.array([97, 255, 255])
        yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)
        
        return yellow_mask
      
    def ground_generate_mask(hsv_frame):
        # 424 version
        low_green = np.array([35, 84, 0])
        high_green = np.array([255, 255, 141])
        green_mask = cv2.inRange(hsv_frame, low_green, high_green)
        
        return green_mask