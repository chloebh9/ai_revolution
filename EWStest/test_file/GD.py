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
            
            kernel = np.ones((3,3),'uint8')

            # 녹색 범위 정의
            low_green = np.array([57, 78, 61])
            high_green = np.array([89, 255, 255])
            green_mask = cv2.inRange(hsv_frame, low_green, high_green)
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

            # 노랑색 범위 정의
            # low_yellow = np.array([0, 16, 144])
            # high_yellow = np.array([43, 184, 255])
            low_yellow = np.array([20, 90, 144])
            high_yellow = np.array([45, 200, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            for green_box in self.green_boxes:
                x, y, w, h = green_box
                green_roi = frame[y:y+h, x:x+w]
                yellow_roi_mask = yellow_mask[y:y+h, x:x+w]
                yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if yellow_contours:
                    cont2 = sorted(yellow_contours, key = cv2.contourArea, reverse = True)[:1]

                    flag_cnt = cont2[0]
                    #check for contour area
                    if (cv2.contourArea(flag_cnt)>100 and cv2.contourArea(flag_cnt)<306000):

                        #Draw a rectange on the contour
                        rect = cv2.minAreaRect(flag_cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        print('flag points :', box)
                        # cv2.drawContours(frame, [box], -1, (0,255,0), 3)

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
                            # 사각형의 중심 계산
                            rect_center_x = np.mean([point[0] for point in box])
                            rect_center_y = np.mean([point[1] for point in box])
                            rect_center = (rect_center_x, rect_center_y)
                            
                            # print('flag points :', box)
                            # # cv2.drawContours(frame, [box], -1, (0,255,0), 3)

                            # f_max_x, f_min_x = self.getMaxMin(box)
                            # f_max_y, f_min_y = self.getyMaxMin(box)
                            # isMiddle = self.judgeMiddle(f_max_x, f_min_x)
                            
                            # frame = self.get_dist(rect, frame, 'flag', isMiddle)
                            
                            cv2.drawContours(green_roi, [box], 0, (0, 255, 0), 2)
                            M = cv2.moments(cnt)
                            if M['m00'] != 0:
                                cx = int(M['m10'] / M['m00'])
                                cy = int(M['m01'] / M['m00'])
                                cv2.putText(frame, 'Flag', (x+cx, y+cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                
                                # flag_centers 리스트에 중점값 추가
                                flag_centers.append((cx, cy))
                                
                                contour_center = (cx, cy)

                                dist = np.sqrt((rect_center[0] - contour_center[0]) ** 2 + (rect_center[1] - contour_center[1]) ** 2)
                                is_flag = dist <= 15

                    # 공 찾기 추가
                    # ball hsv
                    lower1 = np.array([0, 100, 50])
                    upper1 = np.array([10, 200, 200])
                    lower = np.array([137, 0, 0])
                    upper = np.array([200, 255, 255])
                    mask = cv2.inRange(hsv_frame, lower, upper)
                    mask += cv2.inRange(hsv_frame, lower1, upper1)


                    #Remove Extra garbage from image
                    d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations = 5)


                    #find the histogram -> 공
                    cont,hei = cv2.findContours(d_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                    cont = sorted(cont, key = cv2.contourArea, reverse = True)[:1]
                    
                    b_max_x, b_min_x = 0, 0
                    b_max_y, b_min_y = 0, 0
                    
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
                            cv2.drawContours(frame, [box], -1, (255,0,0), 3)

                            b_max_x, b_min_x = self.getMaxMin(box)
                            b_max_y, b_min_y = self.getyMaxMin(box)
                            isMiddle = self.judgeMiddle(b_max_x, b_min_x)
                            
                            # flag_centers가 비어있지 않을 때만 실행
                            if flag_centers:
                                # flag_centers 리스트에서 중점값이 가장 높은 flag 선택
                                farthest_flag_center = min(flag_centers, key=lambda center: center[1])
                                # farthest_flag_center[0] -> x 중점 좌표, farthest_flag_center[1] -> y 중점 좌표
                                # 해당 flag의 박스 그리기
                                # cv2.rectangle(green_roi, (farthest_flag_center[0] - 10, farthest_flag_center[1] - 10),
                                #             (farthest_flag_center[0] + 10, farthest_flag_center[1] + 10), (0, 0, 255), 2)
                                cv2.putText(frame, 'Farthest Flag', (x + farthest_flag_center[0], y + farthest_flag_center[1]),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                # farthest_flag_boxes 리스트에 중점값과 "FLAG" 추가
                                self.farthest_flag_boxes.append((x + farthest_flag_center[0], y + farthest_flag_center[1], "FLAG"))
                                
                                goal_range = 50
                                #공이 있을 때
                                if cont:
                                    # 공이 (홀컵기준)밑에 있을 때
                                    print("여기까지 왔어 1")
                                    if (f_min_y + f_max_y)/2 < (b_min_y + b_max_y)/2:
                                        print("여기도 왔어 1")

                                        if f_min_x + goal_range <= b_min_x and b_max_x <= f_max_x - goal_range and f_min_y <= b_min_y and b_max_y <= f_max_y - goal_range:
                                            print("Goal!")
                                            is_goal = True
                                            cv2.putText(frame, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                                        # 플래그 박스 내부에 공이 존재할 때 골로 인식
                                        elif f_min_x < b_min_x < f_max_x and f_min_y < b_min_y < f_max_y:
                                            print("Goal!")
                                            is_goal = True
                                            cv2.putText(frame, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                                        # 공이 (홀컵기준)위에 있을 때
                                        else:
                                            if f_min_x + goal_range <= b_min_x and b_max_x <= f_max_x - goal_range and f_min_y - goal_range <= b_min_y and b_max_y <= f_max_y - goal_range:
                                                print("Goal!")
                                                is_goal = True
                                                cv2.putText(frame, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)

                                            # return is_goal
                                    # return is_goal
                                else:
                                    print("공을 감지 못했어요")
                        else:
                            print("공의 크기가 올바르지 않아요")
                else:
                    print("yellow_contours 감지 못했어요")

            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        # if self.farthest_flag_boxes:
        #     for box in self.farthest_flag_boxes:
        #         print(f"Farthest Flag Center: {box[0]}, {box[1]}")

        self.cap.release()
        cv2.destroyAllWindows()
        return farthest_flag_center
    
if __name__ == "__main__":
    new_goaldetector = NewGoalDetection()
    new_goaldetector.run()
