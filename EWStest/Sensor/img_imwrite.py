import datetime  # 캡처 이미지나 녹화 영상을 저장할때 현재 일시로 기록하는데 사용할 datetime 모듈을 가져오기.
import cv2  # OpenCV를 사용하기 위해 cv2 모듈을 가져오기.

# 영상 파일을 캡처하기 위해 캡처할 영상파일 경로를 입려한 VideoCapture 객체를 생성합니다.
capture = cv2.VideoCapture(0, cv2.CAP_V4L)
# 녹화할 영상의 코덱을 설정하기 위해 fourcc 변수를 초기화합니다. 여기서는 XVID 코덱을 사용합니다.
fourcc = cv2.VideoWriter_fourcc(*'X264') 
# 녹화 상태를 나타내는 변수로, 초기에는 False로 설정합니다.
record = False

# 무한 반복문을 시작합니다.
while True:

    # 영상에서 하나의 프레임을 읽어옵니다.
    # 'ret'을 제대로 읽었는지 여부를 나타내는 불리언 값이고,
    # 'frame'은 읽어온 프레임입니다.
    ret, frame = capture.read()
    # 읽어온 프레임을 'VideoFrame' 이라는 이름의 창에 표시합니다.
    cv2.imshow("VideoFrame", frame)

    # 현재 날짜와 시간을 'now' 변수에 저장합니다.
    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    
    # 사용자의 키보드 입력을 33밀리초 간격으로 확인합니다.
    key = cv2.waitKey(33)

    # 키보드 입력이 확인되었습니다.
    if key == ord('q'):  # ESC
        break # 프로그램을 종료합니다.
    elif key == ord('c'):  # capture
        print("캡쳐")
        # 프레임을 이미지로 캡처하고 (현재 날짜와 시간).png 형식의 이미지 파일로 저장합니다.
        cv2.imwrite("Video/" + str(now) + ".png", frame)
    elif key == ord('s'):  # start
        print("녹화 시작")
        # 영상 녹화를 시작합니다.
        # 'record' 변수에 True를 저장해서 녹화가 진행되도록 합니다.
        record = True
        # 영상을 저장하는 VideoWriter 객체를 생성합니다.
        # 녹화된 영상 파일 이름은 (현재 날짜와 시간).avi 형식으로 저장합니다.
        # 'fourcc' 변수에 설정한 코덱을 사용합니다. 7번 줄에서 설정했습니다.
        # 초당 프레임 수는 20.0입니다.
        # 마지막 매개변수는 녹화 영상의 너비와 높이로, 녹화할 영상의 너비와 높이를 사용합니다.
        video = cv2.VideoWriter("Video/" + str(now) + ".h264", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
    elif key == ord('e'):  # end
        print("녹화 중지")
        # 'record' 변수에 False를 저장하여 녹화가 중지되도록 합니다.
        record = False
        # VideoWriter 객체를 해제합니다.
        # 녹화가 끝난 후에는 해당 객체를 해제해야 리소스를 반환할 수 있습니다.
        video.release()
        
    # 'record' 변수에 True가 저장되어 있을 경우, 즉 녹화 중인 경우에
    if record == True:
    	# 현재 프레임을 'video' 변수에 설정된 영상에 추가합니다.
    	# 그래서 영상이 녹화되는 동안 프레임이 지속적으로 저장됩니다.
        video.write(frame)

capture.release() # VideoCapture 객체를 해제합니다. 영상 캡처가 끝난 후에는 해당 객체를 해제해야 리소스를 반환할 수 있습니다.
cv2.destroyAllWindows() # 이 프로그램으로 열린 모든 창을 닫습니다.