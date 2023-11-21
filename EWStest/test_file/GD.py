import numpy as np
import cv2

# Open the video file
cap = cv2.VideoCapture(0, cv2.CAP_V4L)

# Filter and font-related variables
kernel = np.ones((5, 5), 'uint8')

while True:
    ret, img = cap.read()
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Color range for red
    lower_red = np.array([0, 0, 50])
    upper_red = np.array([20, 200, 200])
    lower_red2 = np.array([137, 0, 0])
    upper_red2 = np.array([200, 255, 200])
    mask_red = cv2.inRange(hsv_img, lower_red, upper_red)
    mask_red += cv2.inRange(hsv_img, lower_red2, upper_red2)
    r_img = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Color range for green
    lower_green = np.array([38, 100, 61])
    upper_green = np.array([43, 184, 255])
    mask_green = cv2.inRange(hsv_img, lower_green, upper_green)
    g_img = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Color range for yellow
    lower_flag = np.array([20, 90, 144])
            # upper_flag = np.array([43, 184, 255])
    upper_flag = np.array([45, 200, 255])
    mask_yellow = cv2.inRange(hsv_img, lower_flag, upper_flag)
    mask_yellow_in_green = cv2.bitwise_and(mask_yellow, mask_yellow, mask=g_img)
    y_img = cv2.morphologyEx(mask_yellow_in_green, cv2.MORPH_CLOSE, kernel, iterations=11)

    # Find red regions
    cont_r, _ = cv2.findContours(r_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cont_r = sorted(cont_r, key=cv2.contourArea, reverse=True)[:1]

    red_boxes = []

    for cnt in cont_r:
        if 100 < cv2.contourArea(cnt) < 306000:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            red_boxes.append(box)
            cv2.drawContours(img, [box], -1, (0, 0, 255), 3)

    # Find yellow regions within green
    cont_y, _ = cv2.findContours(y_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cont_y = sorted(cont_y, key=cv2.contourArea, reverse=True)[:1]

    yellow_boxes = []

    for cnt in cont_y:
        if 100 < cv2.contourArea(cnt) < 306000:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            yellow_boxes.append(box)
            cv2.drawContours(img, [box], -1, (0, 255, 255), 3)

    # Check if red boxes are inside yellow boxes
    for red_box in red_boxes:
        red_area = cv2.contourArea(red_box)
        for yellow_box in yellow_boxes:
            ret, intersection = cv2.rotatedRectangleIntersection(cv2.minAreaRect(red_box), cv2.minAreaRect(yellow_box))
            if ret == cv2.INTERSECT_FULL or ret == cv2.INTERSECT_PARTIAL:
                intersection_area = cv2.contourArea(intersection)
                if intersection_area / red_area >= 0.6:
                    cv2.putText(img, 'GOAL', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.drawContours(img, [red_box], -1, (0, 0, 255), 3)
                    break

    cv2.imshow('Object Detection', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()