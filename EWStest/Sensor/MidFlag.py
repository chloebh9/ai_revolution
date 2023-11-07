import numpy as np
import cv2

class ShapeRecognition:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        self.green_boxes = []
        self.farthest_flag_box = None

    def process_frame(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 녹색 범위 정의
        low_green = np.array([57, 95, 61])
        high_green = np.array([89, 255, 255])

        # 녹색 범위에 해당하는 부분을 추출
        green_mask = cv2.inRange(hsv_frame, low_green, high_green)

        # 추출된 녹색 부분을 원본 프레임에 표시
        result_frame = cv2.bitwise_and(frame, frame, mask=green_mask)

        # 녹색 영역의 윤곽선 찾기
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 초록 영역 박스 정보 업데이트
        self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

        # 노랑색 범위 정의
        low_yellow = np.array([0, 57, 187])
        high_yellow = np.array([45, 234, 255])

        # 노랑색 범위에 해당하는 부분을 추출
        yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

        shape_info_list = []

        for green_box in self.green_boxes:
            x, y, w, h = green_box
            yellow_roi = yellow_mask[y:y + h, x:x + w]

            try:
                _, labels, stats, centroids = cv2.connectedComponentsWithStats(yellow_roi, connectivity=8)
            except cv2.error as e:
                print(f"OpenCV Error: {e}")
                continue  # 처리를 계속하기 위해 현재 프레임을 건너뛰기

            for i in range(1, len(stats)):
                x_blob, y_blob, w_blob, h_blob, area_blob = stats[i]

                # 영역값이 100픽셀 이하인 영역을 제거
                if area_blob <= 100:
                    continue

                cv2.rectangle(frame, (x + x_blob, y + y_blob), (x + x_blob + w_blob, y + y_blob + h_blob), (0, 255, 0), 2)

                # Convert the yellow region into a binary image for contour detection
                yellow_binary = np.zeros_like(yellow_roi)
                yellow_binary[y_blob:y_blob + h_blob, x_blob:x_blob + w_blob] = yellow_roi[y_blob:y_blob + h_blob, x_blob:x_blob + w_blob]

                # Find contours in the binary image
                yellow_contours, _ = cv2.findContours(yellow_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in yellow_contours:
                    # Approximate the contour to find the vertices
                    epsilon = 0.04 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    num_vertices = len(approx)

                    # Display the shape as ARROW or FLAG based on the number of vertices
                    shape_text = "ARROW" if 7 <= num_vertices <= 8 else "FLAG"

                    # Calculate the center of the yellow region
                    center_x = x + x_blob + w_blob // 2
                    center_y = y + y_blob + h_blob // 2
                    center = (center_x, center_y)

                    # Add shape information to the list
                    shape_info_list.append((center, shape_text))

        # 사용자 정의 조건
        custom_condition = True

        if custom_condition:
            # FLAG로 인식된 박스의 개수가 2개 이상인 경우
            flag_boxes = [box for box in shape_info_list if box[1] == "FLAG"]
            if len(flag_boxes) >= 2:
                # 카메라 화면의 중하단 중앙 좌표
                camera_center = (frame.shape[1] // 2, frame.shape[0])

                # Find the farthest FLAG box among FLAG boxes
                max_distance = 0

                for box in flag_boxes:
                    box_center = box[0]
                    distance = ((box_center[0] - camera_center[0]) ** 2 + (box_center[1] - camera_center[1]) ** 2) ** 0.5

                    if distance > max_distance:
                        max_distance = distance
                        self.farthest_flag_box = box

                # Change the rest of the FLAG boxes to ARROW
                for i, box in enumerate(shape_info_list):
                    if box[1] == "FLAG" and box != self.farthest_flag_box:
                        shape_info_list[i] = (box[0], "ARROW")

        # Print the center coordinates
        if self.farthest_flag_box is not None:
            farthest_center = self.farthest_flag_box[0]
            print(f"Farthest FLAG Center: {farthest_center}")

        # Display centers and shape information on the frame
        for shape_info in shape_info_list:
            center, shape_text = shape_info[0], shape_info[1]
            offset = 10  # Offset to move the text upward
            if shape_text == "FLAG":
                cv2.putText(frame, f'Shape: {shape_text}', (center[0], center[1] - offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f'Shape: {shape_text}', (center[0], center[1] + offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = self.process_frame(frame)

            # Display the original frame
            cv2.imshow('Green and Yellow Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        # Release the video capture and close all OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 0
    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
