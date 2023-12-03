import numpy as np
import cv2

class FlagxCenterMeasurer:
    def __init__(self, video_path=0, img_width=640, img_height=480):
        self.img_width = img_width
        self.img_height = img_height
        self.green_boxes = []
        self.max_x = None
        self.min_x = None
        self.max_y = None
        self.min_y = None
        self.farthest_flag_boxes = []

    def getMaxMin(self, box):
        min_x, max_x = self.img_width, 0
        min_y, max_y = self.img_height, 0

        for x, y in box:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        return max_x, min_x, max_y, min_y

    def check_goal(self, frame, ball_center, flag_boxes):
        for (flag_x, flag_y, _) in flag_boxes:
            if flag_x < ball_center[0] < flag_x + self.img_width / 10 and flag_y < ball_center[1] < flag_y + self.img_height / 10:
                cv2.putText(frame, 'Goal', (int(ball_center[0]), int(ball_center[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임 캡처에 실패했습니다.")
                break

            have_flag = False
            farthest_flag_center = [0, 0]

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            low_green = np.array([35, 84, 0])
            high_green = np.array([255, 255, 141])
            green_mask = cv2.inRange(hsv_frame, low_green, high_green)

            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

            low_yellow = np.array([21, 56, 171])
            high_yellow = np.array([97, 255, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            max_x, min_x = 0, 0

            for green_box in self.green_boxes:
                x, y, w, h = green_box
                green_roi = frame[y:y + h, x:x + w]
                yellow_roi_mask = yellow_mask[y:y + h, x:x + w]
                yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                flag_centers = []

                for cnt in yellow_contours:
                    area = cv2.contourArea(cnt)
                    if area > 10:
                        rect = cv2.minAreaRect(cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        max_x, min_x, max_y, min_y = self.getMaxMin(box)
                        cv2.drawContours(green_roi, [box], 0, (0, 255, 0), 2)
                        M = cv2.moments(cnt)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            cv2.putText(frame, 'Flag', (x + cx, y + cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            flag_centers.append((cx, cy))

                if flag_centers:
                    farthest_flag_center = min(flag_centers, key=lambda center: center[1])
                    cv2.rectangle(green_roi, (farthest_flag_center[0] - 10, farthest_flag_center[1] - 10),
                                  (farthest_flag_center[0] + 10, farthest_flag_center[1] + 10), (0, 0, 255), 2)
                    cv2.putText(frame, 'Farthest Flag', (x + farthest_flag_center[0], y + farthest_flag_center[1]),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    self.farthest_flag_boxes.append((x + farthest_flag_center[0], y + farthest_flag_center[1], "FLAG"))
                    have_flag = True

            # 공에 대한 색상 범위 정의
            red_lower1 = np.array([0, 0, 43])
            red_upper1 = np.array([19, 183, 200])
            red_lower2 = np.array([167, 135, 8])
            red_upper2 = np.array([187, 255, 255])

            # 공에 대한 마스크 생성
            red_mask = cv2.inRange(hsv_frame, red_lower1, red_upper1) + cv2.inRange(hsv_frame, red_lower2, red_upper2)

            # 공의 중심 좌표 계산
            ball_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            ball_centers = []

            for cnt in ball_contours:
                area = cv2.contourArea(cnt)
                if area > 10:
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        ball_centers.append((cx, cy))

            # 플래그 박스와 공의 중심 좌표를 비교하여 골을 확인
            if have_flag:
                self.check_goal(frame, farthest_flag_center, ball_centers)

            cv2.imshow('프레임', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

        if have_flag:
            flag_x_isMiddle = self.judgeMiddle(max_x, min_x)
        else:
            flag_x_isMiddle = "N"

        return [flag_x_isMiddle, farthest_flag_center[0], farthest_flag_center[1], have_flag]

if __name__ == "__main__":
    video_path = 0  # 웹캠을 사용하려면 0을 사용
    shape_recognition = FlagxCenterMeasurer(video_path, img_width=640, img_height=480)
    print(shape_recognition.run())
