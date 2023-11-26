import numpy as np
import cv2

class ShapeRecognition:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Video at {video_path} cannot be opened")
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to grab the first frame")
        self.img_height, self.img_width = frame.shape[:2]
        self.img_width_middle = self.img_width // 2
        self.img_height_middle = self.img_height // 2

    def process_frame(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the color ranges
        green_range = (np.array([57, 78, 61]), np.array([89, 255, 255]))
        yellow_range = (np.array([0, 16, 144]), np.array([43, 184, 255]))
        red_range1 = (np.array([0, 100, 50]), np.array([137, 200, 200]))
        red_range2 = (np.array([137, 0, 0]), np.array([200, 255, 255]))

        # Process green color
        green_mask = cv2.inRange(hsv_frame, *green_range)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        farthest_flag_center = None
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

                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
                        if farthest_flag_center is None or cy < farthest_flag_center[1]:
                            farthest_flag_center = (x + cx, y + cy)

        # Process red color
        red_mask = cv2.inRange(hsv_frame, *red_range1) + cv2.inRange(hsv_frame, *red_range2)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        red_center = None
        for cnt in red_contours:
            area = cv2.contourArea(cnt)
            if area > 100:
                x_red, y_red, w_red, h_red = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x_red, y_red), (x_red + w_red, y_red + h_red), (0, 0, 255), 2)  # Red box

                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    red_center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        return farthest_flag_center, red_center

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            farthest_flag_center, red_center = self.process_frame(frame)

            # Compare the farthest flag center with the red center
            goal_status = "NO GOAL"
            if farthest_flag_center and red_center:
                if np.linalg.norm(np.array(farthest_flag_center) - np.array(red_center)) <= 5:
                    goal_status = "GOAL"

            cv2.putText(frame, goal_status, (self.img_width_middle - 100, self.img_height_middle - 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
