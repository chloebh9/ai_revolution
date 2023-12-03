import numpy as np
import cv2

class NewGoalDetection:
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
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        if not self.cap.isOpened():
            raise ValueError(f"Video cannot be opened")
        self.green_boxes = []
        self.farthest_flag_boxes = []  # 모든 flag의 중점값을 저장하는 리스트

    def get_dist(self, rectange_params, image, name, isMiddle):
        #find no of pixels covered
        pixels = rectange_params[1][0]

        #calculate distance
        dist = (self.img_width * self.focal)/pixels

        image = cv2.putText(image, str(dist), (110,50), self.font,  
        self.fontScale, self.color, 1, cv2.LINE_AA)

        return image
    
    def isGoal(self, ball_box, flag_box):
        ball_max_x, ball_min_x = self.getMaxMin(ball_box)
        ball_max_y, ball_min_y = self.getyMaxMin(ball_box)

        flag_max_x, flag_min_x = self.getMaxMin(flag_box)
        flag_max_y, flag_min_y = self.getyMaxMin(flag_box)

        # 공의 위치가 깃발 경계 내에 있는지 확인
        if ball_min_x >= flag_min_x and ball_max_x <= flag_max_x and ball_min_y >= flag_min_y and ball_max_y <= flag_max_y:
            return True
        else:
            return False

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
        
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            kernel = np.ones((3, 3), 'uint8')

            # 녹색 범위 정의
            low_green = np.array([57, 78, 61])
            high_green = np.array([89, 255, 255])
            green_mask = cv2.inRange(hsv_frame, low_green, high_green)
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

            # 노랑색 범위 정의
            low_yellow = np.array([20, 90, 144])
            high_yellow = np.array([45, 200, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            # 빨강색 범위 정의
            low_red = np.array([0, 100, 100])
            high_red = np.array([10, 255, 255])
            red_mask1 = cv2.inRange(hsv_frame, low_red, high_red)

            low_red = np.array([160, 100, 100])
            high_red = np.array([180, 255, 255])
            red_mask2 = cv2.inRange(hsv_frame, low_red, high_red)

            red_mask = red_mask1 + red_mask2

            for green_box in self.green_boxes:
                x, y, w, h = green_box
                green_roi = frame[y:y+h, x:x+w]
                yellow_roi_mask = yellow_mask[y:y+h, x:x+w]
                yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if yellow_contours:
                    cont2 = sorted(yellow_contours, key=cv2.contourArea, reverse=True)[:1]
                    flag_cnt = max(yellow_contours, key=cv2.contourArea)

                    # check for contour area
                    if (cv2.contourArea(flag_cnt) > 100 and cv2.contourArea(flag_cnt) < 306000):

                        # Draw a rectange on the contour
                        rect = cv2.minAreaRect(flag_cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        print('flag points :', box)

                        f_max_x, f_min_x = self.getMaxMin(box)
                        f_max_y, f_min_y = self.getyMaxMin(box)
                        isMiddle = self.judgeMiddle(f_max_x, f_min_x)

                        frame = self.get_dist(rect, frame, 'flag', isMiddle)

                    # flag의 중점값을 저장하는 리스트
                    flag_centers = []

                    is_flag = False
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

                    # 빨강 공 감지 추가
                    red_mask_roi = red_mask[y:y+h, x:x+w]
                    red_contours, _ = cv2.findContours(red_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if red_contours:
                        for red_cnt in red_contours:
                            red_area = cv2.contourArea(red_cnt)
                            if red_area > 100:  # 일정 면적 이상의 빨강 공 영역만 처리
                                red_rect = cv2.minAreaRect(red_cnt)
                                red_box = cv2.boxPoints(red_rect)
                                red_box = np.int0(red_box)
                                cv2.drawContours(frame, [red_box], 0, (0, 0, 255), 2)

                                # 빨강 공의 중점 계산
                                M = cv2.moments(red_cnt)
                                if M['m00'] != 0:
                                    cx = int(M['m10'] / M['m00'])
                                    cy = int(M['m01'] / M['m00'])
                                    
                                    # 깃발과 빨강 공 중점의 수평 거리 계산
                                    flag_center = max(flag_centers, key=lambda center: center[1])
                                    distance = abs(cx - (x + flag_center[0]))
                                    
                                    # 일정 거리 이내에 있다면 골로 인식
                                    goal_threshold = 20
                                    if distance < goal_threshold:
                                        print("Goal!")
                                        cv2.putText(frame, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    
if __name__ == "__main__":
    new_goaldetector = NewGoalDetection()
    new_goaldetector.run()
