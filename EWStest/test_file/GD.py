import numpy as np
import cv2

class ShapeRecognition:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path, cv2.CAP_V4L)
        if not self.cap.isOpened():
            raise ValueError(f"Video at {video_path} cannot be opened")
        self.green_boxes = []

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # 빨간색 범위 정의
            lower1 = np.array([0, 0, 43])
            upper1 = np.array([19, 183, 200])
            lower2 = np.array([167, 135, 119])
            upper2 = np.array([187, 255, 255])

            # 빨간색 마스크 생성
            red_mask1 = cv2.inRange(hsv_frame, lower1, upper1)
            red_mask2 = cv2.inRange(hsv_frame, lower2, upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
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

                red_roi_mask = red_mask[y:y+h, x:x+w]
                red_contours, _ = cv2.findContours(red_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in red_contours:
                    area = cv2.contourArea(cnt)
                    if area > 10:  # 일정 면적 이상의 영역만 처리
                        rect = cv2.minAreaRect(cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        cv2.drawContours(green_roi, [box], 0, (0, 0, 255), 2)
                        M = cv2.moments(cnt)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            cv2.putText(frame, 'Red Ball', (x+cx, y+cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                            # flag와 빨간 공 중점값 비교
                            for flag_box in yellow_contours:
                                flag_area = cv2.contourArea(flag_box)
                                if flag_area > 10:
                                    flag_rect = cv2.minAreaRect(flag_box)
                                    flag_cx = int(flag_rect[0][0] + x)
                                    flag_cy = int(flag_rect[0][1] + y)

                                    # flag와 빨간 공 중점 좌표 비교
                                    distance = np.sqrt((cx - flag_cx)**2 + (cy - flag_cy)**2)
                                    if distance < 20:  # 일정 거리 이내에 있다면 골로 인식
                                        cv2.putText(frame, 'GOAL', (x+cx, y+cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
