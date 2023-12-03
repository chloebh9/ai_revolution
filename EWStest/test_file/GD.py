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
        
    def is_ball_inside_flag(self, ball_x, ball_y, flag_box):
        # 볼의 중심 좌표가 플래그 박스 내부에 있는지 확인
        flag_x1, flag_y1, flag_x2, flag_y2 = flag_box
        return flag_x1 < ball_x < flag_x2 and flag_y1 < ball_y < flag_y2

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
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

            # 노랑색 범위 정의
            low_yellow = np.array([20, 90, 144])
            high_yellow = np.array([45, 200, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            for green_box in self.green_boxes:
                x, y, w, h = green_box
                green_roi = frame[y:y+h, x:x+w]
                yellow_roi_mask = yellow_mask[y:y+h, x:x+w]
                yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if yellow_contours:
                    cont2 = sorted(yellow_contours, key=cv2.contourArea, reverse=True)[:1]

                    flag_cnt = cont2[0]
                    if 100 < cv2.contourArea(flag_cnt) < 306000:
                        rect = cv2.minAreaRect(flag_cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        f_max_x, f_min_x = self.getMaxMin(box)
                        f_max_y, f_min_y = self.getyMaxMin(box)

                        frame = self.get_dist(rect, frame, 'flag', self.judgeMiddle(f_max_x, f_min_x))

                        flag_centers = []

                        for cnt in yellow_contours:
                            area = cv2.contourArea(cnt)
                            if area > 10:
                                rect = cv2.minAreaRect(cnt)
                                box = cv2.boxPoints(rect)
                                box = np.int0(box)
                                rect_center_x = np.mean([point[0] for point in box])
                                rect_center_y = np.mean([point[1] for point in box])
                                rect_center = (rect_center_x, rect_center_y)

                                cv2.drawContours(green_roi, [box], 0, (0, 255, 0), 2)
                                M = cv2.moments(cnt)
                                if M['m00'] != 0:
                                    cx = int(M['m10'] / M['m00'])
                                    cy = int(M['m01'] / M['m00'])
                                    cv2.putText(frame, 'Flag', (x + cx, y + cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                                    flag_centers.append((cx, cy))

                                    contour_center = (cx, cy)

                                    dist = np.sqrt((rect_center[0] - contour_center[0]) ** 2 + (rect_center[1] - contour_center[1]) ** 2)

                        # 볼 찾기 추가
                        lower1 = np.array([0, 100, 50])
                        upper1 = np.array([10, 200, 200])
                        lower = np.array([137, 0, 0])
                        upper = np.array([200, 255, 255])
                        mask = cv2.inRange(hsv_frame, lower, upper)
                        mask += cv2.inRange(hsv_frame, lower1, upper1)

                        

                        cont, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        cont = sorted(cont, key=cv2.contourArea, reverse=True)[:1]

                        b_max_x, b_min_x = 0, 0
                        b_max_y, b_min_y = 0, 0

                        is_goal = False

                        if len(cont) > 0:
                            ball_cnt = cont[0]

                            if 70 < cv2.contourArea(ball_cnt) < 306000:
                                rect = cv2.minAreaRect(ball_cnt)
                                box = cv2.boxPoints(rect)
                                box = np.int0(box)

                                b_max_x, b_min_x = self.getMaxMin(box)
                                b_max_y, b_min_y = self.getyMaxMin(box)

                                b_center_x, b_center_y = int((b_max_x + b_min_x) / 2), int((b_max_y + b_min_y) / 2)

                                for flag_box in self.green_boxes:
                                    if self.is_ball_inside_flag(b_center_x, b_center_y, flag_box):
                                        is_goal = True
                                        break

                                if is_goal:
                                    print("Goal!")
                                    cv2.putText(frame, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)

                cv2.imshow('Frame', frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    new_goaldetector = NewGoalDetection()
    new_goaldetector.run()
