import numpy as np
import cv2

class GoalDetect:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path, cv2.CAP_V4L)
        if not self.cap.isOpened():
            raise ValueError(f"Video at {video_path} cannot be opened")
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to grab the first frame")
        self.img_height, self.img_width = frame.shape[:2]
        self.img_width_middle = self.img_width // 2
        self.img_height_middle = self.img_height // 2
        self.kernel = np.ones((3, 3), "uint8")

    def process_frame(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        is_goal = True

        # Define the color ranges
        green_range = (np.array([35, 84, 0]), np.array([255, 255, 141]))
        yellow_range = (np.array([13, 56, 124]), np.array([46, 255, 255]))
        red_range1 = (np.array([0, 0, 43]), np.array([19, 183, 200]))
        red_range2 = (np.array([167, 135, 119]), np.array([187, 255, 255]))

        # Process green color
        green_mask = cv2.inRange(hsv_frame, *green_range)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        yellow_outside_green = False  # 초록 상자 외부에 있는 노랑 영역 감지 여부

        for contour in green_contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Process yellow within green
            yellow_mask = cv2.inRange(hsv_frame[y:y+h, x:x+w], *yellow_range)
            yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in yellow_contours:
                area = cv2.contourArea(cnt)
                if area > 10:
                    # If yellow is detected outside green box
                    yellow_outside_green = True
                    break

            if yellow_outside_green:
                break

        # Process red color
        red_mask = cv2.inRange(hsv_frame, *red_range1) + cv2.inRange(hsv_frame, *red_range2)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, self.kernel, iterations=5)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        flag_boxes = []  # 깃발 박스 저장을 위한 리스트
        red_boxes = []  # 빨간색 박스 저장을 위한 리스트

        for cnt in red_contours:
            area = cv2.contourArea(cnt)
            if area > 30:
                x_red, y_red, w_red, h_red = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x_red, y_red), (x_red + w_red, y_red + h_red), (0, 0, 255), 2)  # Red box
                red_boxes.append((x_red, y_red, w_red, h_red))
        
        if flag_boxes and red_boxes == []:
            return None

        # flag_boxes와 red_boxes를 반환합니다.
        return flag_boxes, red_boxes


    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            result = self.process_frame(frame)

            if result == None :
                return 'N'  # 'N'이 반환되면 False를 반환

            flag_boxes, red_boxes = result
            goal_status = "NO GOAL"
            for f_x, f_y, f_w, f_h in flag_boxes:
                for r_x, r_y, r_w, r_h in red_boxes:
                    if (f_x-10 <= r_x <= f_x + f_w+10 and
                        f_x-10 <= r_x + r_w <= f_x + f_w+10 and
                        f_y-10 <= r_y <= f_y + f_h+10 and
                        f_y-10 <= r_y + r_h <= f_y + f_h):
                        goal_status = "GOAL"
                        break
                if goal_status == "GOAL":
                    return True  # 목표가 있을 때 True 반환

        return False  # 루프가 완료되면 False 반환

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = GoalDetect(video_path)
    shape_recognition.run()
