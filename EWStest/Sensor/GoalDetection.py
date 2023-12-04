from HSVAdjust import MaskGenerator
import numpy as np
import cv2

class GoalDetect:
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

    # find the distance from the camera
    def get_dist(self, rectangle_params, image, name, isMiddle):
        # find the number of pixels covered
        pixels = rectangle_params[1][0]

        # calculate distance
        dist = (self.img_width * self.focal) / pixels

        image = cv2.putText(image, str(dist), (110, 50), self.font, self.fontScale, self.color, 1, cv2.LINE_AA)

        return image

    # function to get the maximum and minimum x-coordinates of the box coordinates
    def getMaxMin(self, box):
        min_x, max_x = self.img_width, 0

        for x, y in box:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
        return max_x, min_x

    # function to get the maximum and minimum y-coordinates of the box coordinates
    def getyMaxMin(self, box):
        min_y, max_y = self.img_height, 0

        for x, y in box:
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return max_y, min_y

    # function to check if an object is in the middle based on max_x and min_x
    def judgeMiddle(self, max_x, min_x):
        l_dist = min_x
        r_dist = self.img_width - max_x
        error_range = 30
        
        if abs(l_dist - r_dist) < error_range:
            return True
        else:
            return False

    def process(self):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L)

        # basic constants for opencv functions
        kernel = np.ones((3, 3), 'uint8')

        # Uncomment the following lines if you want to display the window
        # cv2.namedWindow('Object Dist Measure', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('Object Dist Measure', 700, 600)

        # loop to capture video frames
        while True:
            ret, img = cap.read()
            
            if not ret:
                break
            
            hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Mask for the ball
            mask = MaskGenerator.ball_generate_mask(hsv_img)

            # Mask for the yellow flag
            low_yellow = np.array([21, 56, 138])
            high_yellow = np.array([97, 255, 255])
            mask_flag = cv2.inRange(hsv_img, low_yellow, high_yellow)

            lower0 = np.array([23, 144, 151])
            upper0 = np.array([29, 224, 171])
            mask_flag += cv2.inRange(hsv_img, lower0, upper0)

            # Remove extra noise from images
            d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=5)
            f_img = cv2.morphologyEx(mask_flag, cv2.MORPH_OPEN, kernel, iterations=5)

            # Find contours for the ball
            cont, hei = cv2.findContours(d_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cont = sorted(cont, key=cv2.contourArea, reverse=True)[:1]
            
            b_max_x, b_min_x = 0, 0
            b_max_y, b_min_y = 0, 0
            is_goal = False
            
            if len(cont) > 0:
                ball_cnt = cont[0]
                # Check for contour area
                if 4 < len(ball_cnt) < 16 and cv2.contourArea(ball_cnt) > 70 and cv2.contourArea(ball_cnt) < 306000:
                    rect = cv2.minAreaRect(ball_cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    print('ball points:', box)
                    cv2.drawContours(img, [box], -1, (255, 0, 0), 3)

                    b_max_x, b_min_x = self.getMaxMin(box)
                    b_max_y, b_min_y = self.getyMaxMin(box)
                    isMiddle = self.judgeMiddle(b_max_x, b_min_x)
                    
                    img = self.get_dist(rect, img, 'ball', isMiddle)

            # Find contours for the flag
            cont2, hei2 = cv2.findContours(f_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cont2 = sorted(cont2, key=cv2.contourArea, reverse=True)

            if len(cont2) > 0:
                for flag_cnt in cont2:
                    # Check for contour area
                    if 2 < len(flag_cnt) and cv2.contourArea(flag_cnt) > 100:
                        rect = cv2.minAreaRect(flag_cnt)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        print('flag points:', box)
                        cv2.drawContours(img, [box], -1, (0, 255, 0), 3)

                        f_max_x, f_min_x = self.getMaxMin(box)
                        f_max_y, f_min_y = self.getyMaxMin(box)
                        isMiddle = self.judgeMiddle(f_max_x, f_min_x)
                        
                        img = self.get_dist(rect, img, 'flag', isMiddle)
                        
                        print(b_max_x, " ", b_min_x)
                        goal_range = 15
                        
                        # Check if the ball is below the flag
                        if (f_min_y + f_max_y) / 2 < (b_min_y + b_max_y) / 2:
                            if f_min_x + goal_range <= b_min_x and b_max_x <= f_max_x - goal_range and f_min_y <= b_min_y and b_max_y <= f_max_y - goal_range:
                                print("Goal!")
                                is_goal = True
                                cv2.putText(img, 'Goal!', (self.img_width_middle - 200, self.img_height_middle - 200), self.font, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    
            # Uncomment the following lines if you want to display the window
            cv2.imshow('Object Dist Measure', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    goal_detector = GoalDetect()
    print(goal_detector.process())
