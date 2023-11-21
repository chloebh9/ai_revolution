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
            raise ValueError("Video cannot be opened")
        self.green_boxes = []
        self.farthest_flag_boxes = []

    def get_dist(self, rectangle_params, image, name, isMiddle):
        pixels = rectangle_params[1][0]
        dist = (self.img_width * self.focal)/pixels
        image = cv2.putText(image, str(dist), (110,50), self.font,  
                            self.fontScale, self.color, 1, cv2.LINE_AA)
        return image

    def getMaxMin(self, box):
        min_x, max_x = self.img_width, 0
        for x, y in box:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
        return max_x, min_x

    def getyMaxMin(self, box):
        min_y, max_y = self.img_height, 0
        for x, y in box:
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return max_y, min_y

    def judgeMiddle(self, max_x, min_x):
        l_dist = min_x
        r_dist = self.img_width - max_x
        error_range = 30
        return abs(l_dist - r_dist) < error_range
        
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
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in green_contours]

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
                    flag_cnt = sorted(yellow_contours, key=cv2.contourArea, reverse=True)[0]

                    # 공 찾기
                    # ball hsv
                    lower1 = np.array([0, 100, 50])
                    upper1 = np.array([10, 200, 200])
                    lower = np.array([137, 0, 0])
                    upper = np.array([200, 255, 255])
                    mask = cv2.inRange(hsv_frame, lower, upper)
                    mask += cv2.inRange(hsv_frame, lower1, upper1)
                    d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=5)
                    ball_contours, _ = cv2.findContours(d_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    ball_contours = sorted(ball_contours, key=cv2.contourArea, reverse=True)[:1]

                    if ball_contours:
                        ball_cnt = ball_contours[0]
                        ball_rect = cv2.boundingRect(ball_cnt)  # 공의 bounding box

                        flag_rect = cv2.boundingRect(flag_cnt)  # 플래그의 bounding box

                        # 공이 플래그 내에 완전히 들어가 있는지 확인
                        if (flag_rect[0] <= ball_rect[0] <= flag_rect[0] + flag_rect[2] and
                            flag_rect[1] <= ball_rect[1] <= flag_rect[1] + flag_rect[3] and
                            flag_rect[0] <= ball_rect[0] + ball_rect[2] <= flag_rect[0] + flag_rect[2] and
                            flag_rect[1] <= ball_rect[1] + ball_rect[3] <= flag_rect[1] + flag_rect[3]):
                            print("Goal!")
                            cv2.putText(frame, 'Goal!', (50, 50), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)

            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
    
if __name__ == "__main__":
    new_goaldetector = NewGoalDetection()
    new_goaldetector.run()