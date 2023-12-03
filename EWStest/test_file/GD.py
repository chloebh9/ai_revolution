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
            raise ValueError(f"Video cannot be opened")
        self.green_boxes = []
        self.farthest_flag_boxes = []  # 모든 flag의 중점값을 저장하는 리스트

    def get_dist(self, rectange_params, image, name, isMiddle):
        #find no of pixels covered
        pixels = rectange_params[1][0]

        #calculate distance
        dist = (self.img_width * self.focal)/pixels

        image = cv2.putText(image, str(dist), (110,50), self.font,  
        self.fontScale, self.color, 1, cv2.LINE_AA)

        return image

    # box 좌표의 x축 최댓값과 최솟값을 return하는 함수
    def getMaxMin(self, box):
        min_x, max_x = self.img_width, 0

        for x, y in box:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
        return max_x, min_x

    # box 좌표의 y축 최댓값과 최솟값을 return하는 함수
    def getyMaxMin(self, box):
        min_y, max_y = self.img_height, 0

        for x, y in box:
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return max_y, min_y


    # max_x, min_x를 입력받으면 해당 물체가 중간에 있는지 return하는 함수
    def judgeMiddle(self, max_x, min_x):

        l_dist = min_x
        r_dist = self.img_width - max_x
        error_range = 30
        
        if abs(l_dist - r_dist) < error_range:
            return True
        else:
            return False
        
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            kernel = np.ones((3,3),'uint8')

            # 녹색 범위 정의
            low_green = np.array([57, 78, 61])
            high_green = np.array([89, 255, 255])
            green_mask = cv2.inRange(hsv_frame, low_green, high_green)
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

            # 노랑색 범위 정의
            low_yellow = np.array([20, 90, 144])
            high_yellow = np.array([45, 200, 255])
            yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

            yellow_box_coords = []
            for green_box in self.green_boxes:
                x, y, w, h = green_box
                green_roi = frame[y:y+h, x:x+w]
                yellow_roi_mask = yellow_mask[y:y+h, x:x+w]
                yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if yellow_contours:
                    cont2 = sorted(yellow_contours, key = cv2.contourArea, reverse = True)[:1]
                    if cv2.contourArea(cont2[0]) > 100:  # 일정 면적 이상의 영역만 처리
                        rect = cv2.minAreaRect(cont2[0])
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        yellow_box_coords.append(box)

            # 파랑색 상자 좌표
            blue_box_coords = []
            for cont in contours:  # 파랑색 상자로 가정하는 검출된 물체들
                if cv2.contourArea(cont) > 70:  # 일정 면적 이상의 영역만 처리
                    rect = cv2.minAreaRect(cont)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    blue_box_coords.append(box)

            # 파랑색 상자와 노랑색 상자의 좌표 비교
            for yellow_box in yellow_box_coords:
                for blue_box in blue_box_coords:
                    intersection = cv2.pointPolygonTest(yellow_box, (blue_box[0][0], blue_box[0][1]), True)
                    if intersection >= 0:
                        print("Goal!")
                        cv2.putText(frame, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                        break

            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
    
if __name__ == "__main__":
    new_goaldetector = NewGoalDetection()
    new_goaldetector.run()
