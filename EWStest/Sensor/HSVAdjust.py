import numpy as np
import cv2

class MaskGenerator:
    def __init__(self):
        pass
      
    def ball_generate_mask(hsv_img):
        # 424 version
        # lower = np.array([0, 20, 187])
        # upper = np.array([37, 255, 255])
        # lower1 = np.array([118, 0, 0])
        # upper1 = np.array([255, 255, 255])
        
        # 424 version - 2
        # lower = np.array([0, 22, 213])
        # upper = np.array([18, 96, 255])
        # lower1 = np.array([160, 17, 187])
        # upper1 = np.array([255, 255, 255])
        
        # mask1 = cv2.inRange(hsv_img, lower, upper)
        # mask2 = cv2.inRange(hsv_img, lower1, upper1)

        # mask = mask1+mask2
        
        # 동방 version
        lower1 = np.array([0, 0, 43])
        upper1 = np.array([19, 183, 200])
        # lower1 = np.array([0, 100, 50])
        # upper1 = np.array([10, 200, 200])
        lower = np.array([167,135, 119])
        upper = np.array([187, 255, 255])
        mask = cv2.inRange(hsv_img, lower, upper)
        mask += cv2.inRange(hsv_img, lower1, upper1)
        
        # window version
        # lower = np.array([170, 99, 100])
        # upper = np.array([180, 255, 255])
        # mask = cv2.inRange(hsv_img, lower, upper)
        # lower1 = np.array([1, 99, 100])
        # upper1 = np.array([5, 255, 255])
        # mask += cv2.inRange(hsv_img, lower1, upper1)

        # lower_flag = np.array([35, 130, 150])
        # upper_flag = np.array([45, 255, 255])
        # mask_flag = cv2.inRange(hsv_img, lower_flag, upper_flag)

        # mac version
        # lower = np.array([170, 100, 100])
        # upper = np.array([180, 255, 255])
        # mask = cv2.inRange(hsv_img, lower, upper)
        
        # robot version(안쓸듯)
        # lower = np.array([137, 0, 0])
        # upper = np.array([255, 255, 255])
        # lower1 = np.array([0, 66, 87])
        # upper1 = np.array([14, 255, 255])
        
        # mask1 = cv2.inRange(hsv_img, lower, upper)
        # mask2 = cv2.inRange(hsv_img, lower1, upper1)

        # mask = mask1+mask2
        
        return mask

    def flag_generate_mask(hsv_frame):
        # 424 version
        low_yellow = np.array([21, 56, 171])
        high_yellow = np.array([97, 255, 255])
        yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)
        
        # 동방
        # low_yellow = np.array([0, 16, 144])
        # high_yellow = np.array([43, 184, 255])
        
        return yellow_mask
      
    def ground_generate_mask(hsv_frame):
        # 424 version
        low_green = np.array([35, 84, 0])
        high_green = np.array([255, 255, 141])
        green_mask = cv2.inRange(hsv_frame, low_green, high_green)
        
        # low_green = np.array([38, 100, 61])
        # high_green = np.array([86, 255, 255])
        
        return green_mask