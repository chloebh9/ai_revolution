import numpy as np
import cv2

class ShapeRecognition:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path, cv2.CAP_V4L)
        if not self.cap.isOpened():
            raise ValueError(f"Video at {video_path} cannot be opened")
        self.green_boxes = []
        self.farthest_flag_boxes = []  # 모든 flag의 중점값을 저장하는 리스트

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

                # flag의 중점값을 저장하는 리스트
                flag_centers = []

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

                # flag_centers가 비어있지 않을 때만 실행
                if flag_centers:
                    # flag_centers 리스트에서 중점값이 가장 높은 flag 선택
                    farthest_flag_center = min(flag_centers, key=lambda center: center[1])
                    farthest_flag_x, farthest_flag_y = farthest_flag_center

                    # 해당 flag의 박스 그리기
                    farthest_flag_top_left = (x + farthest_flag_x - 10, y + farthest_flag_y - 10)
                    farthest_flag_bottom_right = (x + farthest_flag_x + 10, y + farthest_flag_y + 10)
                    cv2.rectangle(frame, farthest_flag_top_left, farthest_flag_bottom_right, (255, 0, 0), 2)
                    cv2.putText(frame, 'Farthest Flag', (x + farthest_flag_x, y + farthest_flag_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # 가장 멀리 있는 플래그의 ROI 영역 내에서 노랑색이 아닌 부분 검출
                    farthest_flag_roi = yellow_mask[y + farthest_flag_y - 10:y + farthest_flag_y + 10, x + farthest_flag_x - 10:x + farthest_flag_x + 10]
                    non_yellow_mask = cv2.bitwise_not(farthest_flag_roi)
                    non_yellow_contours, _ = cv2.findContours(non_yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for cnt in non_yellow_contours:
                        non_area = cv2.contourArea(cnt)
                        if non_area > 10:  # 일정 면적 이상의 영역만 처리
                            non_rect = cv2.minAreaRect(cnt)
                            non_box = cv2.boxPoints(non_rect)
                            non_box = np.int0(non_box)
                            # 'Farthest Flag' 영역 내부의 노랑색이 아닌 부분에 박스 그리기
                            cv2.drawContours(frame, [non_box], 0, (0, 255, 0), 2)

                                
                red_roi_mask = red_mask[y:y+h, x:x+w]
                red_contours, _ = cv2.findContours(red_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                largest_red_area = 0
                largest_red_center = None

                for cnt in red_contours:
                    area = cv2.contourArea(cnt)
                    if area > largest_red_area:
                        largest_red_area = area
                        M = cv2.moments(cnt)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00']) + x
                            cy = int(M['m01'] / M['m00']) + y
                            largest_red_center = (cx, cy)

                # 가장 큰 빨간색 영역이 farthest_flag_boxes 내에 있는지 확인
                if largest_red_center:
                    red_top_left = (largest_red_center[0] - 10, largest_red_center[1] - 10)
                    red_bottom_right = (largest_red_center[0] + 10, largest_red_center[1] + 10)
                    cv2.rectangle(frame, red_top_left, red_bottom_right, (0, 0, 255), 2)

                    # 'Farthest Flag' 박스와 'Largest Red' 박스의 겹침 확인
                    for flag_box in self.farthest_flag_boxes:
                        flag_x, flag_y, _ = flag_box
                        if (flag_x <= largest_red_center[0] <= flag_x) and (flag_y  <= largest_red_center[1] <= flag_y ):
                            cv2.putText(frame, 'GOAL', largest_red_center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            break
            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        if self.farthest_flag_boxes:
            for box in self.farthest_flag_boxes:
                print(f"Farthest Flag Center: {box[0]}, {box[1]}")

        self.cap.release()
        cv2.destroyAllWindows()
        return farthest_flag_center

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
