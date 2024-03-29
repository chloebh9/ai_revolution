# from Sensor.HSVAdjust import MaskGenerator

import numpy as np
import cv2

class lowestFlag:
    def __init__(self, img_width, img_height):
        self.img_width = img_width
        self.img_height = img_height

    def judgeMiddle(self, ball_center, img_height):
        error_range = 20
        img_height_middle = img_height//2

        is_Middle = img_height_middle - error_range < ball_center[1] < img_height_middle + error_range

        if is_Middle:
            return 'C'
        else:
            if ball_center[1] < img_height_middle:
                return 'U'
            else:
                return 'D'
            
    def run(self):
        your_area_threshold = 300  # 사용자 정의 임계값, 필요에 따라 값을 조정하세요

        cap = cv2.VideoCapture(0,cv2.CAP_V4L)  # 비디오 파일 경로를 설정하세요
        # print("flag_y 시작!!")

        # 초록 영역 박스의 정보를 저장할 리스트
        green_boxes = []
        green_box=[]
        farthest_flag_box = None
        
        farthest_center = -1

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            for i in range(30):
                # 영상을 HSV 색 공간으로 변환
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # 녹색 범위 정의
                # green_mask = MaskGenerator.ground_generate_mask(hsv_frame)
                low_green = np.array([35, 84, 0])
                high_green = np.array([255, 255, 141])
                green_mask = cv2.inRange(hsv_frame, low_green, high_green)


                # 녹색 영역의 윤곽선 찾기
                contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # 초록 영역 박스 정보 업데이트
                green_boxes = [cv2.boundingRect(contour) for contour in contours]

                # yellow_mask = MaskGenerator.flag_generate_mask(hsv_frame)
                # low_yellow = np.array([21, 56, 171])
                # high_yellow = np.array([97, 255, 255])
                # yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)
                low_yellow = np.array([0,105,151])
                high_yellow = np.array([31,255,255])
                yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

                lower0 = np.array( [23 , 144 , 151] )
                upper0 = np.array( [29 , 224 , 171] )
                yellow_mask += cv2.inRange(hsv_frame, lower0 , upper0 )
                lower4 = np.array([ 26 , 74 , 121 ])
                upper4 = np.array([ 32 , 94 , 221 ])
                yellow_mask += cv2.inRange(hsv_frame, lower4 , upper4 )
                lower5 = np.array([ 39 , 72 , 118 ])
                upper5 = np.array([ 45 , 92 , 218 ])
                yellow_mask += cv2.inRange(hsv_frame, lower5 , upper5 )
                lower6 = np.array([ 31 , 77 , 137 ])
                upper6 = np.array([ 37 , 97 , 237 ])
                yellow_mask += cv2.inRange(hsv_frame, lower6 , upper6 )

                shape_info_list = []

                # print("이제 초록색 박스를 잡기 시작하겠습니다.")
                for green_box in green_boxes:
                    x, y, w, h = green_box
                    # print(len(green_boxes))
                    yellow_roi = yellow_mask[y:y + h, x:x + w]
                    # print(len(yellow_roi))
                    # print("주의!")

                    # 초록 상자 내부의 노랑색 영역 처리
                    _, labels, stats, _ = cv2.connectedComponentsWithStats(yellow_roi, connectivity=4)
                    # print("아니넹")
                    for i in range(0, len(stats)):
                        # print("여긴가?")
                        x_blob, y_blob, w_blob, h_blob, area_blob = stats[i]
                        # print("아니었고~")

                        # 영역값이 100픽셀 이하인 영역을 제거
                        if area_blob <= 100:
                            continue
                        
                        # print("초록색 영역안의 작은 노란색을 제거했어요!!")
                        cv2.rectangle(frame, (x + x_blob, y + y_blob), (x + x_blob + w_blob, y + y_blob + h_blob), (0, 255, 0), 2)

                        # Convert the yellow region into a binary image for contour detection
                        yellow_binary = np.zeros_like(yellow_roi)
                        yellow_binary[y_blob:y_blob + h_blob, x_blob:x_blob + w_blob] = yellow_roi[y_blob:y_blob + h_blob, x_blob:x_blob + w_blob]

                        # Find contours in the binary image
                        yellow_contours, _ = cv2.findContours(yellow_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        # print("yellow_contour 시작!")
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
                #             print("노란색 컨투어 하나 확인!")
                # print("화살표와 깃발 구분 완료")

                # 사용자 정의 조건
                custom_condition = True

                if custom_condition:
                    # FLAG로 인식된 박스의 개수가 2개 이상인 경우
                    flag_boxes = [box for box in shape_info_list if box[1] == "FLAG"]
                    if len(flag_boxes) >= 2:
                        # 카메라 화면의 중하단 중앙 좌표
                        camera_center = (frame.shape[1] // 2, frame.shape[0])

                        # Find the farthest FLAG box among FLAG boxes
                        min_distance = float('inf')

                        for box in flag_boxes:
                            box_center = box[0]
                            distance = ((box_center[0] - camera_center[0]) ** 2 + (box_center[1] - camera_center[1]) ** 2) ** 0.5

                            if distance < min_distance:
                                min_distance = distance
                                lowest_flag_box = box

                        # Change the rest of the FLAG boxes to ARROW
                        for i, box in enumerate(shape_info_list):
                            if box[1] == "FLAG" and box != lowest_flag_box:
                                shape_info_list[i] = (box[0], "ARROW")

                # Print the center coordinates
                if lowest_flag_box is not None:
                    lowest_center = lowest_flag_box[0]
                    print(f"lowest FLAG Center: {lowest_center}")

                # Display centers and shape information on the frame
                for shape_info in shape_info_list:
                    center, shape_text = shape_info[0], shape_info[1]
                    offset = 10  # Offset to move the text upward
                    if shape_text == "FLAG":
                        cv2.putText(frame, f'Shape: {shape_text}', (center[0], center[1] - offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, f'Shape: {shape_text}', (center[0], center[1] + offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if lowest_center == -1:
                    continue

                is_y_middle = self.judgeMiddle(lowest_center, self.img_height)
                break

            
            return is_y_middle
        #     cv2.imshow('Green and Yellow Frame', frame)
        #     print(farthest_center)

        #     key = cv2.waitKey(1) & 0xFF
        #     if key == ord('q'):
        #         break
            

                # cap.release()
                # cv2.destroyAllWindows()

if __name__ == "__main__":
    shape_recognition = lowestFlag(img_width=640, img_height=480)
    print(shape_recognition.run())