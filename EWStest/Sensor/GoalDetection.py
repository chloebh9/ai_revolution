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
        is_goal = False

        # Define the color ranges
        green_range = (np.array([57, 78, 61]), np.array([89, 255, 255]))
        yellow_range = (np.array([0, 16, 144]), np.array([43, 184, 255]))
        red_range1 = (np.array([0, 76, 97]), np.array([11, 186, 160]))
        red_range2 = (np.array([137, 0, 0]), np.array([200, 255, 255]))

        # Process green color
        green_mask = cv2.inRange(hsv_frame, *green_range)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        flag_boxes = []  # 깃발 박스 저장을 위한 리스트
        red_boxes = []  # 빨간색 박스 저장을 위한 리스트

        for contour in green_contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Process yellow within green
            yellow_mask = cv2.inRange(hsv_frame[y:y+h, x:x+w], *yellow_range)
            yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in yellow_contours:
                area = cv2.contourArea(cnt)
                if area > 10:
                    x_yellow, y_yellow, w_yellow, h_yellow = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x + x_yellow, y + y_yellow), (x + x_yellow + w_yellow, y + y_yellow + h_yellow), (0, 255, 255), 2)  # Yellow box
                    flag_boxes.append((x + x_yellow, y + y_yellow, w_yellow, h_yellow))

        # Process red color
        red_mask = cv2.inRange(hsv_frame, *red_range1) + cv2.inRange(hsv_frame, *red_range2)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, self.kernel, iterations=5)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in red_contours:
            area = cv2.contourArea(cnt)
            if area > 30:
                x_red, y_red, w_red, h_red = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x_red, y_red), (x_red + w_red, y_red + h_red), (0, 0, 255), 2)  # Red box
                red_boxes.append((x_red, y_red, w_red, h_red))

        return flag_boxes, red_boxes

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            flag_boxes, red_boxes = self.process_frame(frame)

            goal_status = "NO GOAL"
            for f_x, f_y, f_w, f_h in flag_boxes:
                for r_x, r_y, r_w, r_h in red_boxes:
                    if (f_x <= r_x <= f_x + f_w and
                        f_x <= r_x + r_w <= f_x + f_w and
                        f_y <= r_y <= f_y + f_h and
                        f_y <= r_y + r_h <= f_y + f_h):
                        goal_status = "GOAL"
                        break
                if goal_status == "GOAL":
                    is_goal = True
                    break
            return is_goal
            #cv2.putText(frame, goal_status, (self.img_width_middle - 100, self.img_height_middle - 100),
            # cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            #cv2.imshow('Frame', frame)

            #if cv2.waitKey(1) & 0xFF == ord('q'):
                #break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
