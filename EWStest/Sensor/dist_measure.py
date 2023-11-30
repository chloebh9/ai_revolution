from Sensor.HSVAdjust import MaskGenerator

import numpy as np
import cv2

class BallDistanceDetector:
    def __init__(self, camera_index=0, img_width=640, img_height=480, width=4, focal=400, height_robot=33.4):
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        self.img_width = img_width
        self.img_height = img_height
        self.object_width = width
        self.focal_length = focal
        self.height_robot = height_robot
        self.kernel = np.ones((3, 3), 'uint8')
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.org = (0, 20)
        self.font_scale = 0.6
        self.color = (0, 0, 255)
        self.thickness = 2

    def get_distance(self, rectangle_params, image):
        pixels = rectangle_params[1][0]
        dist_robot = int((self.object_width * self.focal_length) / pixels)
        dist_real = (int((dist_robot**2 + self.height_robot**2)**0.5) - 10) * 2

        image = cv2.putText(image, 'Ball Distance from Camera in CM :', self.org, self.font, 1, self.color, 2, cv2.LINE_AA)
        image = cv2.putText(image, str(dist_real), (110, 50), self.font, self.font_scale, self.color, 1, cv2.LINE_AA)
        return image

    def process(self):
        cv2.namedWindow('Object Dist Measure ', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Object Dist Measure ', self.img_width, self.img_height)

        while True:
            ret, img = self.cap.read()
            if not ret:
                break

            hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # ball hsv
            mask = MaskGenerator.ball_generate_mask(hsv_img)

            d_img = cv2.morphologyEx(mask, cv2.MORPH_DILATE, self.kernel, iterations=1)
            cont, _ = cv2.findContours(d_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cont = sorted(cont, key=cv2.contourArea, reverse=True)[:1]

            for cnt in cont:
                if 100 < cv2.contourArea(cnt) < 306000:
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(img, [box], -1, (255, 0, 0), 3)
                    img = self.get_distance(rect, img)

            cv2.imshow('Object Dist Measure ', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        self.cap.release()

# # Usage
# detector = BallDistanceDetector(camera_index=0)
# detector.process_video()

if __name__ == "__main__":
    dist_detector = BallDistanceDetector()
    print(dist_detector.process())



# # 공의 거리를 검출하는 코드 (distReal)

# # -*- coding: utf-8 -*-
# import numpy as np
# import cv2
# import time

# #Define object specific variables  
# distRobot = 0
# distReal = 0
# focal = 400
# pixels = 0
# width = 4
# heightBall = 4
# heightRobot = 10

# #find the distance from then camera
# def get_dist(rectange_params,image, name):
#     #find no of pixels covered
#     pixels = rectange_params[1][0]
#     print(pixels)
#     #calculate distance
#     distRobot = int((width*focal)/(pixels))
#     distReal = (int((distRobot**2+heightRobot**2)**(1/2))-10)*2

#     image = cv2.putText(image, 'ball Distance from Camera in CM :', org, font, 1, color, 2, cv2.LINE_AA)

#     image = cv2.putText(image, str(distReal), (110,50), font, fontScale, color, 1, cv2.LINE_AA)


#     return image

# #Extract Frames 
# cap = cv2.VideoCapture(0,  cv2.CAP_V4L)


# #basic constants for opencv Functs
# kernel = np.ones((3,3),'uint8')
# font = cv2.FONT_HERSHEY_SIMPLEX 
# org = (0,20)  
# fontScale = 0.6 
# color = (0, 0, 255) 
# thickness = 2


# cv2.namedWindow('Object Dist Measure ',cv2.WINDOW_NORMAL)
# cv2.resizeWindow('Object Dist Measure ', 700,600)


# #loop to capture video frames
# while True:
#     ret, img = cap.read()

#     hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)


#     #공 색상값
#     # lower = np.array([137, 0, 0])
#     # upper = np.array([255, 255, 255])
#     # mask = cv2.inRange(hsv_img, lower, upper)
    
#     # ball hsv
#     lower1 = np.array([0, 100, 50])
#     upper1 = np.array([10, 200, 200])
#     lower = np.array([137, 0, 0])
#     upper = np.array([200, 255, 255])
#     mask = cv2.inRange(hsv_img, lower, upper)
#     mask += cv2.inRange(hsv_img, lower1, upper1)

#     #Remove Extra garbage from image
#     d_img = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel,iterations = 1)

#     #find the histogram
#     cont,hei = cv2.findContours(d_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#     cont = sorted(cont, key = cv2.contourArea, reverse = True)[:1]

#     for cnt in cont:
#         #check for contour area
#         if (cv2.contourArea(cnt)>100 and cv2.contourArea(cnt)<306000):

#             #Draw a rectange on the contour
#             rect = cv2.minAreaRect(cnt)
#             box = cv2.boxPoints(rect) 
#             box = np.int0(box)
#             print('points :', box)
#             cv2.drawContours(img,[box], -1,(255,0,0),3)
            
#             img = get_dist(rect,img, 'ball')



#     cv2.imshow('Object Dist Measure ', img)


#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break



# cv2.destroyAllWindows()