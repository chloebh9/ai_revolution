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

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            farthest_flag_box = None
            red_in_farthest_flag = False

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            low_green = np.array([35, 82, 0])
            high_green = np.array([152, 255, 141])
            green_mask = cv2.inRange(hsv_frame, low_green, high_green)

            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            green_boxes = [cv2.boundingRect(contour) for contour in contours]

            low_yellow = np.array([21, 58, 126])
            high_yellow = np.array([34, 255, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            shape_info_list = []

            for green_box in green_boxes:
                x, y, w, h = green_box
                yellow_roi = yellow_mask[y:y + h, x:x + w]

                _, labels, stats, _ = cv2.connectedComponentsWithStats(yellow_roi, connectivity=4)

                for i in range(0, len(stats)):
                    x_blob, y_blob, w_blob, h_blob, area_blob = stats[i]

                    if area_blob <= 100:
                        continue

                    cv2.rectangle(frame, (x + x_blob, y + y_blob), (x + x_blob + w_blob, y + y_blob + h_blob), (0, 255, 255), 2)  # Yellow box for flags

                    yellow_binary = np.zeros_like(yellow_roi)
                    yellow_binary[y_blob:y_blob + h_blob, x_blob:x_blob + w_blob] = yellow_roi[y_blob:y_blob + h_blob, x_blob:x_blob + w_blob]

                    yellow_contours, _ = cv2.findContours(yellow_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for contour in yellow_contours:
                        epsilon = 0.04 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        num_vertices = len(approx)

                        shape_text = "ARROW" if 7 <= num_vertices <= 8 else "FLAG"

                        center_x = x + x_blob + w_blob // 2
                        center_y = y + y_blob + h_blob // 2
                        center = (center_x, center_y)

                        shape_info_list.append((center, shape_text))

            custom_condition = True

            if custom_condition:
                flag_boxes = [box for box in shape_info_list if box[1] == "FLAG"]
                if len(flag_boxes) >= 2:
                    camera_center = (frame.shape[1] // 2, frame.shape[0])

                    max_distance = 0

                    for box in flag_boxes:
                        box_center = box[0]
                        distance = ((box_center[0] - camera_center[0]) ** 2 + (box_center[1] - camera_center[1]) ** 2) ** 0.5

                        if distance > max_distance:
                            max_distance = distance
                            farthest_flag_box = box

                    for i, box in enumerate(shape_info_list):
                        if box[1] == "FLAG" and box != farthest_flag_box:
                            shape_info_list[i] = (box[0], "ARROW")

                    farthest_center = farthest_flag_box[0]

                red_lower1 = np.array([0, 0, 43])
                red_upper1 = np.array([19, 183, 200])
                red_lower2 = np.array([167, 135, 8])
                red_upper2 = np.array([187, 255, 255])

                red_mask = cv2.inRange(hsv_frame, red_lower1, red_upper1) + cv2.inRange(hsv_frame, red_lower2, red_upper2)
                red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in red_contours:
                    area = cv2.contourArea(cnt)
                    if area > 0:
                        x_red, y_red, w_red, h_red = cv2.boundingRect(cnt)
                        red_center = (x_red + w_red // 2, y_red + h_red // 2)

                        if (farthest_center[0] - 10 <= red_center[0] <= farthest_center[0] + 10 and
                                farthest_center[1] - 10 <= red_center[1] <= farthest_center[1] + 10):
                            cv2.rectangle(frame, (x_red, y_red), (x_red + w_red, y_red + h_red), (0, 0, 255), 2)  # Red box for red area
                            red_in_farthest_flag = True
                            #break

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = GoalDetect(video_path)
    shape_recognition.run()
