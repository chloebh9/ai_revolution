import cv2
import numpy as np

class ColorTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture("C:/Users/eowkd/OneDrive/Desktop/ai_revolution/EWStest/Sensor/VIDEO/real3.avi")
        cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)  # 트랙바 창 크기를 조절 가능하게 설정
        cv2.resizeWindow("Tracking", 400, 200)  # 창의 초기 크기를 설정

        self.create_trackbars()
        self.paused = False
        self.frame = None

    def create_trackbars(self):
        # # 노랑 임시 색상
        # cv2.createTrackbar("LH", "Tracking", 17, 255, self.nothing)
        # cv2.createTrackbar("LS", "Tracking", 130, 255, self.nothing)
        # cv2.createTrackbar("LV", "Tracking", 134, 255, self.nothing)                              
        # cv2.createTrackbar("UH", "Tracking", 43, 255, self.nothing)
        # cv2.createTrackbar("US", "Tracking", 255, 255, self.nothing)
        # cv2.createTrackbar("UV", "Tracking", 255, 255, self.nothing)

        cv2.createTrackbar("LH", "Tracking", 107, 255, self.nothing)
        cv2.createTrackbar("LS", "Tracking", 62, 255, self.nothing)
        cv2.createTrackbar("LV", "Tracking", 127, 255, self.nothing)                              
        cv2.createTrackbar("UH", "Tracking", 223, 255, self.nothing)
        cv2.createTrackbar("US", "Tracking", 255, 255, self.nothing)
        cv2.createTrackbar("UV", "Tracking", 255, 255, self.nothing)
        # # 녹색 임시 색상
        # cv2.createTrackbar("LH", "Tracking", 62, 255, self.nothing)
        # cv2.createTrackbar("LS", "Tracking", 64, 255, self.nothing)
        # cv2.createTrackbar("LV", "Tracking", 118, 255, self.nothing)
        # cv2.createTrackbar("UH", "Tracking", 128, 255, self.nothing)
        # cv2.createTrackbar("US", "Tracking", 255, 255, self.nothing)
        # cv2.createTrackbar("UV", "Tracking", 255, 255, self.nothing)

        # 빨강 임시 색상
        # cv2.createTrackbar("LH", "Tracking", 107, 255, self.nothing)
        # cv2.createTrackbar("LS", "Tracking", 62, 255, self.nothing)
        # cv2.createTrackbar("LV", "Tracking", 127, 255, self.nothing)
        # cv2.createTrackbar("UH", "Tracking", 223, 255, self.nothing)
        # cv2.createTrackbar("US", "Tracking", 255, 255, self.nothing)
        # cv2.createTrackbar("UV", "Tracking", 255, 255, self.nothing)

    def nothing(self, x):
        pass

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.hsv_value = self.hsv[y, x]
            self.mouse_x, self.mouse_y = x, y

    def track(self):
        self.hsv_value = (0, 0, 0)
        self.mouse_x, self.mouse_y = 0, 0

        while True:
            if not self.paused:
                _, frame = self.cap.read()
                if not _:
                    break
                else:
                    self.hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    l_b, u_b = self.get_trackbar_values()
                    mask = cv2.inRange(self.hsv, l_b, u_b)
                    res = cv2.bitwise_and(frame, frame, mask=mask)

                text = f"HSV: {self.hsv_value}"
                cv2.putText(res, text, (self.mouse_x, self.mouse_y + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (135, 60, 200), 1)

                self.frame = res

            cv2.imshow("Mask", mask)
            cv2.imshow("Result", self.frame)
            cv2.setMouseCallback("Result", self.mouse_callback)

            key = cv2.waitKey(100)
            if key == ord('a'):
                self.paused = not self.paused
                if self.paused:
                    print("일시정지")
            if key & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def get_trackbar_values(self):
        lh = cv2.getTrackbarPos("LH", "Tracking")
        ls = cv2.getTrackbarPos("LS", "Tracking")
        lv = cv2.getTrackbarPos("LV", "Tracking")
        uh = cv2.getTrackbarPos("UH", "Tracking")
        us = cv2.getTrackbarPos("US", "Tracking")
        uv = cv2.getTrackbarPos("UV", "Tracking")
        return np.array([lh, ls, lv]), np.array([uh, us, uv])

if __name__ == "__main__":
    tracker = ColorTracker()
    tracker.track()
