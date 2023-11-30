# 공이 있는지 없는지 판별하는 코드 (is_ball)
# from Sensor.HSVAdjust import MaskGenerator

# -*- coding: utf-8 -*-
import numpy as np
import cv2


class FindBall:
    def __init__(self, img_width=640, img_height=480, width=4, focal=450):
        self.kernel = np.ones((3, 3), "uint8")
        # self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.org = (0, 20)
        self.fontScale = 0.6

    def process(self):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        # cv2.namedWindow('Object Dist Measure ', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('Object Dist Measure ', 700, 600)

        while True:
            ret, img = cap.read()
            dilimg = cv2.dilate(img, self.kernel, iterations=1)
            hsv_img = cv2.cvtColor(dilimg, cv2.COLOR_BGR2HSV)
            
            # mask = MaskGenerator.ball_generate_mask(hsv_img)
            lower = np.array([0, 22, 213])
            upper = np.array([25, 96, 255])
            lower1 = np.array([160, 17, 187])
            upper1 = np.array([255, 255, 255])
            
            mask1 = cv2.inRange(hsv_img, lower, upper)
            mask2 = cv2.inRange(hsv_img, lower1, upper1)

            mask = mask1+mask2

            # 모폴로지 연산
            # d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=5)

            cont, hei = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cont = sorted(cont, key=cv2.contourArea, reverse=True)[:1]

            ball_box = None

            is_ball = False  # 공이 인식되어 있는지를 나타내는 변수
            for cnt in cont:
                if cv2.contourArea(cnt) > 100 and cv2.contourArea(cnt) < 306000:
                    is_ball = True

            cv2.imshow("Object Dist Measure ", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

            # print(is_ball)
            # break
        return is_ball


if __name__ == "__main__":
    findBall = FindBall()
    findBall.process()
