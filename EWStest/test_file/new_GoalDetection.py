#MidFlag.py에서 가져온 깃발과 홀컵 구분 코드를 GoalDetection.py에 합치려고 시도 한 것..이지만 망함

import numpy as np
import cv2

class ShapeRecognition:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path, cv2.CAP_V4L)
        if not self.cap.isOpened():
            raise ValueError(f"Video at {video_path} cannot be opened")
        self.green_boxes = []
        self.farthest_flag_boxes = []  # 모든 flag의 중점값을 저장하는 리스트

    # 깃발의 박스 영역 데이터를 반환하는 메서드 추가
    def get_flag_boxes(self):
        return self.farthest_flag_boxes
      
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 녹색 범위 정의
            low_green = np.array([57, 78, 61])
            high_green = np.array([89, 255, 255])
            green_mask = cv2.inRange(hsv_frame, low_green, high_green)
            result_frame = cv2.bitwise_and(frame, frame, mask=green_mask)
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

            # 노랑색 범위 정의
            low_yellow = np.array([0, 16, 144])
            high_yellow = np.array([43, 184, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            for green_box in self.green_boxes:
                x, y, w, h = green_box
                green_roi = frame[y:y+h, x:x+w]
                yellow_roi_mask = yellow_mask[y:y+h, x:x+w]
                yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # flag의 중점값을 저장하는 리스트
                flag_centers = []

                for cnt in yellow_contours:
                    # 영역의 면적 계산
                    area = cv2.contourArea(cnt)
                    if area > 10:  # 일정 면적 이상의 영역만 처리
                        rect = cv2.minAreaRect(cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        cv2.drawContours(green_roi, [box], 0, (0, 255, 0), 2)
                        M = cv2.moments(cnt)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            cv2.putText(frame, 'Flag', (x+cx, y+cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                            # flag_centers 리스트에 중점값 추가
                            flag_centers.append((cx, cy))

                # flag_centers가 비어있지 않을 때만 실행
                if flag_centers:
                    # flag_centers 리스트에서 중점값이 가장 높은 flag 선택
                    farthest_flag_center = min(flag_centers, key=lambda center: center[1])
                    # 해당 flag의 박스 그리기
                    cv2.rectangle(green_roi, (farthest_flag_center[0] - 10, farthest_flag_center[1] - 10),
                                  (farthest_flag_center[0] + 10, farthest_flag_center[1] + 10), (0, 0, 255), 2)
                    cv2.putText(frame, 'Farthest Flag', (x + farthest_flag_center[0], y + farthest_flag_center[1]),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    # farthest_flag_boxes 리스트에 중점값과 "FLAG" 추가
                    self.farthest_flag_boxes.append((x + farthest_flag_center[0], y + farthest_flag_center[1], "FLAG"))

            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        if self.farthest_flag_boxes:
            for box in self.farthest_flag_boxes:
                print(f"Farthest Flag Center: {box[0]}, {box[1]}")

        self.cap.release()
        cv2.destroyAllWindows()
        return farthest_flag_center
      
class GoalDetect:
    def __init__(self, img_width=640, img_height=480, width=4, focal=450):
        self.dist = 0 
        self.focal = focal
        self.pixels = 30
        self.width = width

        self.img_width = img_width
        self.img_height = img_height
        self.img_width_middle = img_width // 2
        self.img_height_middle = img_height // 2

        self.kernel = np.ones((3, 3), 'uint8')
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.org = (0, 20)
        self.fontScale = 0.6
        self.color = (0, 0, 255)
        self.thickness = 2
        
        self.middle = img_width // 2

    # 깃발의 박스 영역을 비교하는 메서드 추가
    def is_valid_flag(self, detected_flag_box, shape_recognition_flag_boxes):
        for _, _, _, w1, h1 in shape_recognition_flag_boxes:
            w2, h2 = detected_flag_box[2], detected_flag_box[3]
            area_difference = abs((w1 * h1) - (w2 * h2))
            if area_difference <= 50:
                return True
        return False
      
    #find the distance from then camera
    def get_dist(self, rectange_params, image, name, isMiddle):
        #find no of pixels covered
        pixels = rectange_params[1][0]

        #calculate distance
        dist = (self.img_width * self.focal)/pixels

        image = cv2.putText(image, str(dist), (110,50), self.font,  
        self.fontScale, self.color, 1, cv2.LINE_AA)

        return image

    # box 좌표의 x축 최댓값과 최솟값을 return하는 함수
    def getMaxMin(self, box):
        min_x, max_x = self.img_width, 0

        for x, y in box:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
        return max_x, min_x

    # box 좌표의 y축 최댓값과 최솟값을 return하는 함수
    def getyMaxMin(self, box):
        min_y, max_y = self.img_height, 0

        for x, y in box:
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return max_y, min_y


    # max_x, min_x를 입력받으면 해당 물체가 중간에 있는지 return하는 함수
    def judgeMiddle(self, max_x, min_x):

        l_dist = min_x
        r_dist = self.img_width - max_x
        error_range = 30
        
        if abs(l_dist - r_dist) < error_range:
            return True
        else:
            return False

    def process(self):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L)

        #basic constants for opencv Functs
        kernel = np.ones((3,3),'uint8')

        # imshow 실행시 주석 빼기
        cv2.namedWindow('Object Dist Measure ', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Object Dist Measure ', 700,600)

        #loop to capture video frames
        while True:
            ret, img = cap.read()
            
            if not ret:
                break
            
            hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            
            # 깃발 및 홀컵 탐지
            detected_objects = []  # 탐지된 객체의 박스 정보 저장

            # window version
            # ball hsv
            lower1 = np.array([0, 100, 50])
            upper1 = np.array([10, 200, 200])
            lower = np.array([137, 0, 0])
            upper = np.array([200, 255, 255])
            mask = cv2.inRange(hsv_img, lower, upper)
            mask += cv2.inRange(hsv_img, lower1, upper1)

            lower_flag = np.array([20, 90, 144])
            # upper_flag = np.array([43, 184, 255])
            upper_flag = np.array([45, 200, 255])
            mask_flag = cv2.inRange(hsv_img, lower_flag, upper_flag)


            #Remove Extra garbage from image
            d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel,iterations = 5)
            f_img = cv2.morphologyEx(mask_flag, cv2.MORPH_OPEN, kernel,iterations = 5)


            #find the histogram -> 공
            cont,hei = cv2.findContours(d_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cont = sorted(cont, key = cv2.contourArea, reverse = True)[:1]
            
            b_max_x, b_min_x = 0, 0
            b_max_y, b_min_y = 0, 0
            
            # 깃발 및 홀컵 구분 및 골인 판별 로직
            for obj_box in detected_objects:
                if self.is_valid_flag(obj_box, shape_recognition_flag_boxes):
                    # 깃발로 판별된 경우, 추가 처리
                    continue
                else:
                    # 홀컵으로 판별된 경우, 골인 여부 판별
                    # 골인 판별 로직
                    # ...
                    
            is_goal = False
            
            if len(cont) > 0:
                ball_cnt = cont[0]
                #check for contour area
                if (cv2.contourArea(ball_cnt)>70 and cv2.contourArea(ball_cnt)<306000):
                    
                    #Draw a rectange on the contour
                    rect = cv2.minAreaRect(ball_cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    print('ball points :', box)
                    cv2.drawContours(img, [box], -1, (255,0,0), 3)

                    b_max_x, b_min_x = self.getMaxMin(box)
                    b_max_y, b_min_y = self.getyMaxMin(box)
                    isMiddle = self.judgeMiddle(b_max_x, b_min_x)
                    
                    img = self.get_dist(rect, img, 'ball', isMiddle)

            # 깃발
            cont2,hei2 = cv2.findContours(f_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cont2 = sorted(cont2, key = cv2.contourArea, reverse = True)[:1]

            if len(cont2) > 0:
                flag_cnt = cont2[0]
                #check for contour area
                if (cv2.contourArea(flag_cnt)>100 and cv2.contourArea(flag_cnt)<306000):

                    #Draw a rectange on the contour
                    rect = cv2.minAreaRect(flag_cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    print('flag points :', box)
                    cv2.drawContours(img, [box], -1, (0,255,0), 3)

                    f_max_x, f_min_x = self.getMaxMin(box)
                    f_max_y, f_min_y = self.getyMaxMin(box)
                    isMiddle = self.judgeMiddle(f_max_x, f_min_x)
                    
                    img = self.get_dist(rect,img, 'flag', isMiddle)
                    
                    print(b_max_x, " ", b_min_x)
                    # goal_range = 22
                    # # 공이 (홀컵기준)밑에 있을 때
                    # if (f_min_y + f_max_y)/2 < (b_min_y + b_max_y)/2:
                    #     if f_min_x + goal_range <= b_min_x and b_max_x <= f_max_x - goal_range and f_min_y <= b_min_y and b_max_y <= f_max_y - goal_range:
                    #         print("Goal!")
                    #         is_goal = True
                    #         cv2.putText(img, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    #         # return is_goal
                    # # 공이 (홀컵기준)위에 있을 때
                    # else:
                    #     if f_min_x + goal_range <= b_min_x and b_max_x <= f_max_x - goal_range and f_min_y - goal_range <= b_min_y and b_max_y <= f_max_y - goal_range:
                    #         print("Goal!")
                    #         is_goal = True
                    #         cv2.putText(img, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    #         # return is_goal
                        
            return is_goal
                
        #     imshow 실행시 주석 빼기
        #     cv2.imshow('Object Dist Measure ', img)

        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

        # cv2.destroyAllWindows()
        
    # 깃발이 유효한지 여부를 판별하는 메서드
    def is_valid_flag(self, detected_flag_box, shape_recognition_flag_boxes):
        for _, _, _, w1, h1 in shape_recognition_flag_boxes:
            w2, h2 = detected_flag_box[2], detected_flag_box[3]
            area_difference = abs((w1 * h1) - (w2 * h2))
            if area_difference <= 50:
                return True
        return False
        
# if __name__ == "__main__":
#     goal_detector = GoalDetect()
#     print(goal_detector.process())

# if __name__ == "__main__":
#     video_path = 0  # Use 0 for webcam
#     shape_recognition = ShapeRecognition(video_path)
#     shape_recognition.run()
    
if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam

    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
    flag_boxes_from_shape_recognition = shape_recognition.get_flag_boxes()

    goal_detector = GoalDetect()
    # GoalDetect 클래스에서 is_valid_flag 메서드를 사용하여 깃발 판별
    goal_detector.process(flag_boxes_from_shape_recognition)

