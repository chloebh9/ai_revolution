import cv2
import numpy as np
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0, cv2.CAP_V4L)

img_width = 640
img_height = 480

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임 캡처에 실패했습니다.")
        break

    red = (0, 0, 255)
    cv2.line(frame, (img_width//2, 0), (img_width//2, img_height), red, 5)
    cv2.line(frame, (0, img_height//2), (img_width, img_height//2), red, 5)

    cv2.imshow('dst', frame)
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
