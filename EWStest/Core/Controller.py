# -*- coding: utf-8 -*-
from enum import Enum, auto
from Core.Robo import Robo
from Sensor.search_ball import FindBall  # 공이 있으면 true, 없으면 false
from Sensor.ball_y_center import BallyCenterMeasurer  # 공이 가운데, 위, 아래 중 어디에 있는지 (C, U, D)
from Sensor.ball_x_center import BallxCenterMeasurer  # 공이 가운데, 왼쪽, 오른쪽 중 어디에 있는지 (C, L, R)
from Sensor.tan_dist_measure import DistMeasurer  # 로봇에서부터 공과의 거리
from Sensor.t_put_judge import Tputting_y_BallCenterMeasurer  # 공이 Y축 기준으로 가운데 있을 때 true, 아니면 false
from Sensor.t_put_x_judge import Tputting_x_BallCenterMeasurer  # 공이 X축 기준으로 가운데 있을 때 true, 아니면 false
from Sensor.flag_x_center import FlagxCenterMeasurer  # 깃발이 가운데, 왼쪽, 오른쪽 중 어디에 있는지 (C, L, R)
from Sensor.flag_y_center import FlagyCenterMeasurer  # 깃발이 가운데, 위, 아래 중 어디에 있는지 (C, U, D)
from Sensor.HitPoint import HitPointer  # 타격지점 구하는 코드
from Sensor.GoalDetection import GoalDetect # 홀인 했는지 확인하는 코드
from Sensor.putting_flag_check import PuttingFlagxCenterMeasurer
import time
import copy
from collections import Counter


class Act(Enum):
    START = auto()  # 시작 - 아무런 동작도 안 함
    SEARCH_FIRST = auto()  # T샷 시작
    SEARCH_FLAG = auto()  # 깃발 찾기
    SEARCH_BALL = auto()  # 공 찾기
    SEARCH_PUTTING_LOCATION = auto()  # 치는 위치 찾기
    CHECK = auto()  # 홀인 확인
    EXIT = auto()  # 종료
    TEST = auto() # 테스트때 사용


# 상황 판단 하는 파트
class Controller:
    robo: Robo = Robo()
    #act: Act = Act.START  # 순서도 시작
    act: Act = Act.CHECK
    # act: Act = Act.START가 시작 지점

    count_putting: int = 0  # 퍼팅 횟수
    check_holein: int = 0  # 홀인 판단 횟수
    area: str = ""  # 현재 맵
    ball: bool  # 공 T/F

    # T샷할 때 사용하는 위치 파악하는 변수 위치가 파악되면 그 위치의 변수가 1이 된다.
    L_right: int = 0  # 로봇: L / 공: right
    L_center: int = 0  # 로봇: L / 공: center
    L_left: int = 0  # 로봇: L / 공: left
    C_right: int = 0  # 로봇: C / 공: right
    C_center: int = 0  # 로봇: C / 공: center
    C_left: int = 0  # 로봇: C / 공: left
    
    # check_flag_distance에서 쓰이는 깃발 센터 각도
    flag_angle_x: int = 0
    flag_angle_y: int = 0
    
    # check_ball_distance에서 쓰이는 공 센터 각도
    ball_angle_x: int = 0
    ball_angle_y: int = 0
    
    flag_stop: bool = False  # 깃발 찾을 때, 끝 각도에서 더 깃발이 끝에 있을 때 한 발자국 뒤로 가는 코드에서 쓰이는 판단 변수
    ball_stop: bool = False  # 공 찾을 때, 끝 각도에서 더 공이 끝에 있을 때 한 발자국 뒤로 가는 코드에서 쓰이는 판단 변수
    
    canPutting: float = 11.0  # 칠 수 있는 거리있는지 판단 변수 (길이)
    
    check_angle: int = 0  # art.check 부분에서 깃발 거리값 가져오기 위한 변수

    ###################################################################################################
    # 티샷에서 공이 어디에 있는지 확인하는 코드
    @classmethod
    def check_ball_first(self):
        L_right = self.L_right  # 로봇: L / 공: right
        L_center = self.L_center  # 로봇: L / 공: center
        L_left = self.L_left  # 로봇: L / 공: left
        C_right = self.C_right  # 로봇: C / 공: right
        C_center = self.C_center  # 로봇: C / 공: center
        C_left = self.C_left  # 로봇: C / 공: left
        NO = self.No

        #  .process():  공에 유무를 반환함 T/F
        dir_list = [25, 43, 55, 67]  # 임의로 지정한 로봇 머리의 각도 값 (실제 경기장에서 다시 설정해야 할 수도..)
        dir = 3  # dir_list에서 90을 고를 수 있도록 설정하는 값
        cnt = 0  # 로봇이 어디에서 찾았는지 구분하는 변수

        time.sleep(1)  # 함수를 실행할 때 오류가 안 나도록 하는 time.sleep

        # 로봇이 왼쪽에 있다고 가정
        Tput_y_center = Tputting_y_BallCenterMeasurer().process()
        for i in range(3):  # 티샷이 3개이므로 3번 반복
            self.robo._motion.set_head("DOWN", dir_list[dir])  # 고개 내리면서 확인
            dir -= 1
            time.sleep(0.1)
            Tput_y_center = Tputting_y_BallCenterMeasurer().process()
            print("Ball find and center T/F: ", Tput_y_center)  # 공 센터의 T/F값 출력

            if Tput_y_center == False:  # 공이 발견되지 않았을 때
                cnt += 1

            elif Tput_y_center == True:  # 공이 발견됐을 때
                print("공을 찾았습니다.")
                if cnt == 0:
                    self.L_right = 1
                    print("LEFT: 공을 오른쪽에서 찾았습니다.")
                elif cnt == 1:
                    self.L_center = 1
                    print("LEFT: 공을 가운데에서 찾았습니다.")
                elif cnt == 2:
                    self.L_left = 1
                    print("LEFT: 공을 왼쪽에서 찾았습니다.")
                break

            else:
                print("왼쪽 위치에 있지 않거나, 문제가 있을 수 있습니다.")
                print("로봇이 가운데 위치한다고 생각하고 시작하겠습니다.")

        # 로봇이 가운데 있다고 가정
        dir = 0
        self.robo._motion.set_head("DOWN", dir_list[dir])

        if Tput_y_center == False:
            print("로봇이 가운데에 있다고 생각하겠습니다.")
            Tput_x_center = Tputting_x_BallCenterMeasurer().process()
            print("Ball find and x center T/F: ", Tput_x_center)

            if Tput_x_center == True:
                if cnt == 3:
                    print("Center: 공을 가운데에서 찾았습니다.")
                    self.C_center = 1
                    return
                    
            elif Tput_x_center == False:
                print("가운데 가운데 X")
                self.robo._motion.set_head("LEFT", 54)
                time.sleep(0.1)
                find_ball = FindBall().process()

                time.sleep(0.1)
                cnt += 1

                if find_ball == True:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                    if cnt == 4:
                        print("Center: 공을 왼쪽에서 찾았습니다.")
                        self.C_left = 1
                        return

                print("가운데 왼쪽 X")
                self.robo._motion.set_head("RIGHT", 49)
                time.sleep(0.1)
                find_ball = FindBall().process()
                print("공의 유무: ", find_ball)
                time.sleep(0.1)
                cnt += 1
                
                if find_ball == True:
                    if cnt == 5:
                        print("Center: 공을 오른쪽에서 찾았습니다.")
                        self.C_right = 1
                        return

            else:
                print("티샷 부분에서 공을 어디서도 찾지 못했습니다.")
                self.No = 1
                return 
                        
    ###################################################################################################
    # 깃발이 있는지 찾는 코드
    @classmethod
    def check_flag(self):
        down_y = [80, 30, 60] # 깃발 찾기 위한 Y축
        right_left = [30, 45, 60] # 일단 모션에 있는 값 넣었는데, 확인하고 바꿔야 함..
        
        flag = FlagxCenterMeasurer(img_width=640, img_height=480)
        find_flag = flag.run()
        
        print("find_flag: ", find_flag)
        
        y_dir = 0
        while find_flag[3] != True:   # 깃발을 못 찾았을 때 (find_flag[3]: have_flag)
            print("깃발 찾는 함수(check_flag) 실행")
            print("find_flag[3] (have_flag): ", find_flag[3])
            
            find_flag = flag.run()
            x_dir = 0
            self.robo._motion.set_head("DOWN", down_y[y_dir])
            y_dir += 1
            time.sleep(0.2)
            
            if y_dir == len(down_y):
                break
        
            global tmp_angle
            # 고개 오른쪽으로 찾기
            for i in range(len(right_left)):
                find_flag = FlagxCenterMeasurer(img_width=640, img_height=480).run()
                time.sleep(0.1)
                print(find_flag)

                if find_flag[3] == True:
                    print("깃발을 찾았습니다.")
                    break

                print("깃발이 안 보여 오른쪽부터 찾겠습니다.")
                self.robo._motion.set_head("RIGHT", right_left[x_dir])
                
                # 깃발이 고개 끝보다 더 오른쪽에 있을 때, 한 발자국 뒤로 감
                if right_left[-1] == right_left[x_dir]:
                    flag_is_where = FlagxCenterMeasurer(img_width=640, img_height=480).run()
                    if flag_is_where[0] == "R":
                        self.robo._motion.walk("BACKWARD")
                        print("flag_is_where[0]: ", flag_is_where[0])
                        print("깃발이 시야보다 더 오른쪽에 있어 한 발자국 뒤로 감")
                        self.flag_stop = True
                        return
                
                print("Debug: ", right_left[x_dir])
                print("=============================")
                x_dir += 1
                time.sleep(0.2)
                if (find_flag == True) or (x_dir == len(right_left)):
                    tmp_angle = right_left[x_dir-2]
                    break
            self.robo._motion.set_head("LEFTRIGHT_CENTER") # 고개 원위치로 (가운데로)
            time.sleep(0.2)
            
            if find_flag[3] == True:
                print("깃발을 오른쪽에서 최종적으로 찾았습니다.")
                break

            x_dir = 0
            # 고개 왼쪽으로 찾기
            for i in range(len(right_left)):
                find_flag = FlagxCenterMeasurer(img_width=640, img_height=480).run()
                time.sleep(0.1)

                print("깃발이 안 보여 왼쪽부터 찾겠습니다.")
                self.robo._motion.set_head("LEFT", right_left[x_dir])
                
                # 깃발이 고개 끝보다 더 왼쪽에 있을 때, 한 발자국 뒤로 감
                if right_left[-1] == right_left[x_dir]:
                    flag_is_where = FlagxCenterMeasurer(img_width=640, img_height=480).run()
                    if flag_is_where[0] == "L":
                        self.robo._motion.walk("BACKWARD")
                        print("flag_is_where[0]: ", flag_is_where[0])
                        print("깃발이 시야보다 더 왼쪽에 있어 한 발자국 뒤로 감")
                        self.flag_stop = True
                        return
                
                print("Debug: ", right_left[x_dir])
                print("=============================")
                x_dir += 1
                time.sleep(0.2)
                if (find_flag == True) or (x_dir == len(right_left)):
                    tmp_angle = -right_left[x_dir-2]
                    print("self.robo._motion.x_head_angle: ", tmp_angle)
                    break
            self.robo._motion.set_head("LEFTRIGHT_CENTER") # 고개 원위치로 (가운데로)
            time.sleep(0.2)
            
            if find_flag[3] == False:
                self.robo._motion.walk("BACKWARD")  # 깃발 못 찾으면 한 발자국 뒤로 가도록
                continue
            
            # 로봇 머리 각도 저장
            if tmp_angle < 0:  # 로봇 머리 각도가 왼쪽에
                best_angle = self.find_best(abs(tmp_angle))  # 들어온 값이 마이너스이므로 플러스로 바꾸기
                self.robo._motion.set_head("LEFT", best_angle)
                self.robo._motion.x_head_angle = tmp_angle  # 저장된 각도를 돌린 각도로 바꾸기
                print("!!!로봇 머리 각도 왼쪽!!!!!!: ", self.robo._motion.x_head_angle)
                break
            elif tmp_angle > 0:   # 로봇 머리 각도가 오른쪽에
                best_angle = self.find_best(tmp_angle)
                self.robo._motion.set_head("RIGHT", best_angle)
                self.robo._motion.x_head_angle = tmp_angle
                print("!!!로봇 머리 각도 왼쪽!!!!!!: ", self.robo._motion.x_head_angle)
                break
            else:
                print("로봇 머리 각도는 정면입니다.")
                print("!!!로봇 머리 각도 가운데!!!!!!: ", self.robo._motion.x_head_angle)
                break
            
            

            # 여기까지 오면 깃발을 찾은 상황 -> 깃발 센터 맞추는 함수로 넘어가기
            self.check_flag_distance()
                
    ###################################################################################################
    # 깃발 1도씩 조정하면서 각도 확인
    @classmethod
    def check_flag_distance(self):
        # flagxcenter = FlagxCenterMeasurer(img_width=640, img_height=480)
        # flagycenter = FlagyCenterMeasurer(img_width=640, img_height=480)

        correctAngle = 0  # 깃발이 센터에 왔을 때 1로 변경

        # 깃발을 못 찾았을 때 반환하는 값

        while correctAngle != 1:
            flag_x_angle = FlagxCenterMeasurer(img_width=640, img_height=480).run()
            time.sleep(0.2)
            if flag_x_angle[0] == "N":
                down_y = self.find_best(self.robo._motion.y_head_angle - 45)
                self.robo._motion.set_head("DOWN", down_y)
            print("check_flag_distance에서의 flag_x_angle: ", flag_x_angle[0])
            print("flag_x_angle[0] == C: ", flag_x_angle[0] == "C")

            if flag_x_angle[0] == "C":
                print("통과했어요")
                flag_y_angle = FlagyCenterMeasurer(img_width=640, img_height=480).run()
                print(flag_y_angle[0])
                time.sleep(0.2)

                if flag_y_angle[0] == "C":
                    print("flag_x_angle: ", flag_x_angle[0])
                    print("flag_y_angle: ", flag_y_angle[0])
                    print("중앙에 있습니다.")
                    correctAngle = 1
                    break

                elif flag_y_angle[0] == "D" or flag_y_angle[0] == "U":
                    recent_will_angle = 3
                    lst_UD = ["hi"]  # 인덱스 에러 방지
                    while flag_y_angle[0] != "C":
                        before_flag_y_angle = copy.copy(flag_y_angle[0])
                        flag_y_angle = FlagyCenterMeasurer(img_width=640, img_height=480).run()  # 여기서 U/C/D 판단
                        time.sleep(0.2)
                        print("flag_y: ", flag_y_angle[0])  # 판단 내용 출력

                        if before_flag_y_angle != flag_y_angle[0]:
                            recent_will_angle = 2
                        
                        # 반복 고치기: 반복값이 n번 이상일 때, 그 값으로 설정
                        cnt_UD = Counter(lst_UD)
                        result = cnt_UD.most_common()
                        # print("result: ", result)
                        if result[0][1] >= 3:  # 최빈값이 나온 개수
                            self.flag_angle_y = result[0][0]
                            correctAngle = 1
                            print("반복 멈춘 후의 저장된 self.flag_angle_y: ", self.flag_angle_y)
                            break

                        if flag_y_angle[0] == "U":  # 판단 내용 판단
                            self.robo._motion.set_head_small("UP", recent_will_angle)
                            tmp = self.robo._motion.y_head_angle
                            lst_UD.append(tmp)

                        if flag_y_angle[0] == "D":  # 판단 내용 판단
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                            tmp = self.robo._motion.y_head_angle
                            lst_UD.append(tmp)

                    correctAngle = 1
                    print("중앙에 왔습니다.")
                    break

                else:
                    print("check_flag_distance 함수에서 원하는 Y angle이 안 들어왔습니다.")
                    self.robo._motion.set_head("DOWN", 55)

            elif flag_x_angle[0] == "L" or flag_x_angle[0] == "R":
                print("flag_x_angle: R or L이 들어왔습니다.")
                print(flag_x_angle[0])
                recent_will_angle = 3
                lst_LR = ["hi"]  # 인덱스 에러 방지
                while flag_x_angle[0] != "C":
                    print("while문이 실행되었습니다.")
                    before_flag_x_angle = copy.copy(flag_x_angle[0])
                    flag_x_angle = FlagxCenterMeasurer(img_width=640, img_height=480).run()  # 여기서 U/C/D 판단
                    time.sleep(0.2)
                    print("flag_x: ", flag_x_angle[0])  # 판단 내용 출력

                    if before_flag_x_angle != flag_x_angle[0]:
                        recent_will_angle = 2
                    
                    # 깃발 찾고, 센터 맞추다가 깃발을 잃어버린 경우 break하고 다시 깃발을 찾도록
                    if flag_x_angle[0] == 'N':
                        break
                        
                    # 반복 고치기: 반복값이 n번 이상일 때, 그 값으로 설정
                    cnt_LR = Counter(lst_LR)
                    result = cnt_LR.most_common()
                    # print("result: ", result)
                    if result[0][1] >= 3:  # 최빈값이 나온 개수
                            self.flag_angle_x = result[0][0]
                            correctAngle = 1
                            print("반복 멈춘 후의 저장된 self.flag_angle_x: ", self.flag_angle_x)
                            break

                    if flag_x_angle[0] == "L":
                        self.robo._motion.set_head_small("LEFT", recent_will_angle)
                        tmp = self.robo._motion.x_head_angle
                        lst_LR.append(tmp)
                    if flag_x_angle[0] == "R":
                        self.robo._motion.set_head_small("RIGHT", recent_will_angle)
                        tmp = self.robo._motion.x_head_angle
                        lst_LR.append(tmp)
            else:
                print("flag_ball_distance 함수에서 원하는 X angle이 안 들어왔습니다.")
                        
    ###################################################################################################
    # 공 찾는 코드 + 공 1도씩 조정하면서 각도 확인하는 함수
    @classmethod
    def check_ball_distance(self):
        correctAngle = 0  # 공이 센터에 왔을 때 1로 변경

        ballxcenter = BallxCenterMeasurer(img_width=640, img_height=480)
        ballycenter = BallyCenterMeasurer(img_width=640, img_height=480)
        
        # 공을 못 찾았을 때 반환하는 값
        ball_x_angle = ["N", "N", "N"]
        ball_y_angle = ["N"]
        ball_rl = "N"
        
        # 공과 로봇의 거리(dist)와 공이랑 깃발 사이의 각도(flag_ball_angle_fin), 방향(direction)을 구하는 부분
        flag_angle = self.robo._motion.x_head_angle  # 깃발 각도 저장
        down_y = [30, 50, 80] # 공 찾기 위한 Y축
        right_left = [30, 45, 54, 60] # 일단 모션에 있는 값 넣었는데, 확인하고 바꿔야 함..
        find_ball = FindBall().process()
        
        
        print("ball_x_angle[0]: ", ball_x_angle[0] == "N") # Debug
        print("find_ball (T/F): ", find_ball) # 공 찾는거 T/F
        
        if ball_x_angle[0] == "N":
            y_dir = 0
            while find_ball != True:
                print("find_ball", find_ball)
                x_dir = 0
                self.robo._motion.set_head("DOWN", down_y[y_dir])
                y_dir += 1
                time.sleep(0.2)
                if y_dir == len(down_y):
                    return False # 공을 아예 못 찾을 시, 그냥 false return
                    break
        
                # 고개 오른쪽으로 찾기
                for i in range(len(right_left)):
                    find_ball = FindBall().process()
                    time.sleep(0.1)
                    print("공이 안 보여 오른쪽부터 찾겠습니다.")
                    self.robo._motion.set_head("RIGHT", right_left[x_dir])
                    
                    # 공이 고개 끝보다 더 오른쪽에 있을 때, 한 발자국 뒤로 감
                    if right_left[-1] == right_left[x_dir]:
                        ball_is_where = BallxCenterMeasurer().process()
                        if ball_is_where[0] == "R":
                            self.robo._motion.walk("BACKWARD")
                            print("ball_is_where[0]: ", ball_is_where[0])
                            print("공이 시야보다 더 오른쪽에 있어 한 발자국 뒤로 감")
                            self.ball_stop = True
                            return
                        
                    print("Debug(right): ", right_left[x_dir])
                    print("=============================")
                    x_dir += 1
                    time.sleep(0.2)
                    if x_dir == len(right_left):
                        break
                    elif find_ball == True:
                        print("오른쪽에서 찾았습니다.")
                        ball_rl = "R"
                        break
                time.sleep(0.2)

                find_ball = FindBall().process()
                print("find_ball: ", find_ball)
                # print(x_dir)

                if find_ball == True:
                    print("최종적으로 오른쪽에서 찾았습니다.")
                    break
                
                x_dir = 0
                # 고개 왼쪽으로 찾기
                for i in range(len(right_left)):
                    find_ball = FindBall().process()
                    time.sleep(0.1)
                    print("공이 안 보여 왼쪽부터 찾겠습니다.")
                    self.robo._motion.set_head("LEFT", right_left[x_dir])
                    
                    # 공이 고개 끝보다 더 왼쪽에 있을 때, 한 발자국 뒤로 감
                    if right_left[-1] == right_left[x_dir]:
                        ball_is_where = BallxCenterMeasurer().process()
                        if ball_is_where[0] == "L":
                            self.robo._motion.walk("BACKWARD")
                            print("공이 시야보다 더 왼쪽에 있어 한 발자국 뒤로 감")
                            self.ball_stop = True
                            return
                        
                    print("Debug(left): ", right_left[x_dir])
                    print("=============================")
                    x_dir += 1
                    time.sleep(0.2)
                    if x_dir == len(right_left):
                        break
                    elif find_ball == True:
                        print("왼쪽에서 찾았습니다.")
                        ball_rl = "L"
                        break

                time.sleep(0.2)
            # 여기까지 오면 공을 찾은 상황
 
        # 공 센터 맞추는 부분
        while correctAngle != 1:
            print("공 센터 맞추는 부분")
            ball_x_angle = ballxcenter.process()
            # if ball_x_angle[0] == "N":
            #     y_dir += 1
            #     self.robo._motion.set_head("DOWN", down_y[y_dir])
            time.sleep(0.2)
            print("ball_x_angle: ", end="")
            print(ball_x_angle[0])
            print("이 부분")

            # x축 기준으로 센터라면, y축 기준으로 센터를 맞추기
            if ball_x_angle[0] == "C":
                print("여기 들어옴.")
                ball_y_angle = ballycenter.process()
                time.sleep(0.2)
                if ball_y_angle[0] == "C":
                    print("ball_x_angle: ", ball_x_angle[0])
                    print("ball_y_angle: ", ball_y_angle[0])
                    print("중앙에 왔습니다.")
                    correctAngle = 1
                    break

                elif ball_y_angle[0] == "D" or ball_y_angle[0] == "U":
                    # 아래로 1도씩 움직이기
                    recent_will_angle = 3
                    lst_UD = ["hi"]  # 인덱스 에러 방지
                    while ball_y_angle[0] != "C":
                        before_ball_y_angle = copy.copy(ball_y_angle[0])
                        ball_y_angle = ballycenter.process()
                        time.sleep(0.2)
                        print("ball_y: ", ball_y_angle[0])

                        if before_ball_y_angle != ball_y_angle[0]:
                            recent_will_angle = 2
                            
                        # 반복 고치기: 반복값이 n번 이상일 때, 그 값으로 설정
                        cnt_UD = Counter(lst_UD)
                        result = cnt_UD.most_common()
                        # print("result: ", result)
                        if result[0][1] >= 3:  # 최빈값이 나온 개수
                            self.ball_angle_y = result[0][0]
                            correctAngle = 1
                            print("반복 멈춘 후의 저장된 self.flag_angle_y: ", self.flag_angle_y)
                            break

                        if ball_y_angle[0] == "U":
                            self.robo._motion.set_head_small("UP", recent_will_angle)
                            tmp = self.robo._motion.y_head_angle
                            lst_UD.append(tmp)

                        if ball_y_angle[0] == "D":
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                            tmp = self.robo._motion.y_head_angle
                            lst_UD.append(tmp)

                    correctAngle = 1
                    print("중앙에 왔습니다.")
                
                    # 공 센터 맞추면 해당 각도 저장
                    self.ball_angle = self.robo._motion.x_head_angle
                    print("공을 센터에 맞추고, 각도를 저장하였습니다.")
                    print("=============================")
                
                    # 공 센터 맞추면 로봇과 공의 거리 구하는 코드 실행
                    dist_Process = DistMeasurer()
                    self.dist = dist_Process.display_distance(self.ball_angle)  # dist: 공과 로봇의 거리 ?? self.dist에 대한 정의가 없는데 어떻게 씀?
                    time.sleep(0.1)
                
                    # flag_ball_angle_fin: 공이랑 깃발 사이의 각도
                    self.flag_ball_angle_fin = abs(self.ball_angle - flag_angle)
                    print("공이랑 깃발 각도를 저장하였습니다.")
                    print("=============================")
                                
                    # direction: 방향
                    if (self.ball_angle - flag_angle) > 0:
                        direction = "R"
                    elif (self.ball_angle - flag_angle) < 0:
                        direction = "L"
                    else:
                        direction = ""  # 여기 나오면 안 되긴 함..
                    print("방향을 저장하였습니다.")
                    print("=============================")
                    
                    break

                else:
                    print("check_ball_distance 함수에서 원하는 Y angle이 안 들어옴.")

            # x축 기준으로 공의 센터가 안 맞는다면 실행 (여기여기)
            elif ball_x_angle[0] == "L" or ball_x_angle[0] == "R":
                recent_will_angle = 3
                lst_LR = ["hi"]  # 인덱스 에러 방지
                while ball_x_angle[0] != "C":
                    before_ball_x_angle = copy.copy(ball_x_angle[0])
                    ball_x_angle = ballxcenter.process()
                    time.sleep(0.2)
                    print("ball_x: ", ball_x_angle[0])

                    if before_ball_x_angle != ball_x_angle[0]:
                        recent_will_angle = 2
                    
                    # 공을 찾고, 센터 맞추다가 공을 잃어버린 경우 break하고 다시 공을 찾도록
                    if ball_x_angle[0] == 'N':
                        break
                        
                    # 반복 고치기: 반복값이 n번 이상일 때, 그 값으로 설정
                    cnt_LR = Counter(lst_LR)
                    result = cnt_LR.most_common()
                    # print("result: ", result)
                    if result[0][1] >= 3:  # 최빈값이 나온 개수
                        self.ball_angle_x = result[0][0]
                        correctAngle = 1
                        print("반복 멈춘 후의 저장된 self.ball_angle_x: ", self.ball_angle_x)
                        break

                    if ball_x_angle[0] == "L":
                        self.robo._motion.set_head_small("LEFT", recent_will_angle)
                        tmp = self.robo._motion.x_head_angle
                        lst_LR.append(tmp)
                        
                    elif ball_x_angle[0] == "R":
                        self.robo._motion.set_head_small("RIGHT", recent_will_angle)
                        tmp = self.robo._motion.x_head_angle
                        lst_LR.append(tmp)
                        
                    elif ball_x_angle[0] == "N":
                        if ball_rl == "L":
                            self.robo._motion.set_head_small("LEFT", recent_will_angle)
                        elif ball_rl == "R":
                            self.robo._motion.set_head_small("RIGHT", recent_will_angle)

            else:
                print("check_ball_distance 함수에서 원하는 X angle이 안 들어옴.")
                
    ###################################################################################################
    # 공이 가운데, 오른쪽, 왼쪽 중 어디에 있는지 확인해서 로봇을 옆으로(왼쪽, 오른쪽) 움직이는 모션 (walk_side)
    @classmethod
    def ball_feature_ball(self):
        print("Debug in ball_feature_ball")
        ball_is_x_center = ["N", "N", "N"]  # fix
        # [공의 가운데 여부, 공의 x 중심좌표, 공의 y 중심좌표]

        # ball_ball_feature_measure 에서 return 값: L / C / R
        while ball_is_x_center[0] != "C":
            ball_is_x_center = BallxCenterMeasurer().process()
            print("카메라 기준(공): ", ball_is_x_center[0])  # 카메라 기준(공): L or C or R

            if ball_is_x_center[0] == "L":
                print("공이 왼쪽에 있습니다.")
                self.robo._motion.walk_side("LEFT")
                time.sleep(0.5)

            elif ball_is_x_center[0] == "C":
                print("공이 가운데 있습니다.")
                break

            elif ball_is_x_center[0] == "R":
                print("공이 오른쪽에 있습니다.")
                self.robo._motion.walk_side("RIGHT")
                time.sleep(0.5)
            else:
                print("원하는 값이 반환되지 않았습니다.")
                
###################################################################################################
    # 로봇 몸체랑 깃발이랑 일직선 만들기
    @classmethod
    def putting_robot_turn(self):
        # 여기까지 오면 깃발 찾고, 센터까지 맞춘 상황
        if self.robo._motion.x_head_angle != 0:
            print("체크",self.robo._motion.x_head_angle)
            if self.robo._motion.x_head_angle < 0:  # 로봇 머리 각도가 왼쪽에 있음
                print("Turn Right")
                angle = self.find_best(abs(self.robo._motion.x_head_angle))
                print("TEST find_best_angle: ", angle)
                self.robo._motion.turn("LEFT", angle)
                time.sleep(0.1)
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.1)
            elif self.robo._motion.x_head_angle > 0:  # 로봇 머리 각도가 오른쪽에 있음
                print("Turn Left")
                angle = self.find_best(abs(self.robo._motion.x_head_angle))
                print("TEST find_best_angle: ", angle)
                self.robo._motion.turn("RIGHT", angle)
                time.sleep(0.1)
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.1)
            else:
                print("None 값이 나와서 오류남")
                return
        else:  # 로봇 몸체와 깃발이 일직선
            print("Turn Center")
            return
    ###################################################################################################
    # 들어온 앵글값에서 가장 가까운(최적의) 값을 리턴 하는 함수
    @classmethod
    def find_best(self, target_angle):
        # target_angle: 로봇과 깃발을 일직선으로 맞추기 위해 틀어야 하는 각도
        actions = [60, 45, 20, 10, 3]  # 가능한 동작 리스트
        remaining_angle = target_angle
        best_action = None
        
        while remaining_angle > 0 and actions:
            best_action = min(actions, key=lambda x: abs(target_angle - x))
            if best_action <= remaining_angle:
                remaining_angle -= best_action
            actions.remove(best_action)
            
            if best_action is not None:
                return best_action
            else:
                return "best_action: N"
            
    ###################################################################################################
    # 걸어갈 때, 틀어질 경우를 대비해서 다시 위치 잡는 함수
    @classmethod
    def correct_position(self):
        # 공을 못 찾았을 때 반환하는 값
        ball_x_angle = ["N", "N", "N"]

        xTput_x_center = BallxCenterMeasurer(img_width=640, img_height=480)
        ball_x_angle = xTput_x_center.process()

        # 걸어가면서 틀어진 각도 맞추는 로직
        while ball_x_angle[0] != "C":
            print("걸어가면서 틀어진 각도 맞추기")

        while ball_x_angle[0] != "C":
            if ball_x_angle[0] == "L" or ball_x_angle[0] == "R":
                if ball_x_angle[0] == "L":
                    self.robo._motion.set_head_small("LEFT", 2)

                if ball_x_angle[0] == "R":
                    self.robo._motion.set_head_small("RIGHT", 2)

        # 현재 머리 각도가 플러스면 오른쪽으로 턴해야 함
        while self.robo._motion.x_head_angle > 0:
            self.robo._motion.x_head_angle = head_plus(60)
            self.robo._motion.x_head_angle = head_plus(45)
            self.robo._motion.x_head_angle = head_plus(20)
            self.robo._motion.x_head_angle = head_plus(10)
            self.robo._motion.x_head_angle = head_plus(3)
            self.robo._motion.x_head_angle = 0

        # 현재 머리 각도가 마이너스면 왼쪽으로 턴해야 함
        while self.robo._motion.x_head_angle < 0:
            self.robo._motion.x_head_angle = head_minus(60)
            self.robo._motion.x_head_angle = head_minus(45)
            self.robo._motion.x_head_angle = head_minus(20)
            self.robo._motion.x_head_angle = head_minus(10)
            self.robo._motion.x_head_angle = head_minus(3)
            self.robo._motion.x_head_angle = 0

        # 오른쪽으로 턴
        def head_plus(N):
            x_head_angle_n = self.robo._motion.x_head_angle // N
            if x_head_angle_n >= 1:
                for _ in range(x_head_angle_n):
                    self.robo._motion.turn("RIGHT", N)
                    self.robo._motion.x_head_angle -= N
            elif x_head_angle_n == 0:
                return self.robo._motion.x_head_angle
            else:
                print("여기로 오면 안 되는뎁..")
            return self.robo._motion.x_head_angle

        # 왼쪽으로 턴
        def head_minus(N):
            x_head_angle_n = self.robo._motion.x_head_angle // -N
            if x_head_angle_n >= 1:
                for _ in range(x_head_angle_n):
                    self.robo._motion.turn("LEFT", N)
                    self.robo._motion.x_head_angle += N
            elif x_head_angle_n == 0:
                return self.robo._motion.x_head_angle
            else:
                print("여기로 오면 안 되는뎁..")
            return self.robo._motion.x_head_angle
        
    ###################################################################################################
    # 퍼팅 후 타격지점 찾을 때, 들어온 앵글값에서 가장 가까운(최적의) 값을 찾아 턴 하는 함수
    @classmethod
    def find_best_actions(self, target_angle, way):
    # target_angle: 로봇이 퍼팅 위치 가기 전 틀어야하는 각도
    # way: 공이 왼쪽에 있는지 오른쪽에 있는지 판단하는 값
        actions = [60, 45, 20, 10, 3]  # 가능한 동작 리스트
        remaining_angle = abs(target_angle)
        robot_way = way
        best_actions = []

        while remaining_angle > 0 and actions:
            # 각도와 가장 가까운 값을 선택
            best_action = min(actions, key=lambda x: abs(remaining_angle - x))

            if best_action <= remaining_angle:
                # 최적의 동작을 실행
                best_actions.append(best_action)

                if target_angle > 0:
                    self.robo._motion.turn("RIGHT", best_action)
                    print(f"{best_action}도 실행")

                elif target_angle < 0:
                    self.robo._motion.turn("LEFT", best_action)
                    print(f"{best_action}도 실행")

                else:
                    print("way의 값이 이상함.")

                remaining_angle -= best_action
                time.sleep(0.8)

            actions.remove(best_action)
                
    ###################################################################################################
    # 퍼팅 후 공 위치 찾기
    @classmethod
    def check_ball_location(self):
        print("Debug check_ball_location in Controller")
        time.sleep(0.1)

        # 구간을 나눠서 찾는다고 생각
        short_left_location = 0  # 짧은 거리 왼쪽
        short_right_location = 0  # 짧은 거리 오른쪽
        short_forward_location = 0  # 짧은 거리 정면
        long_forward_location = 0  # 긴 거리 정면
        long_left_location = 0  # 긴 거리 왼쪽
        long_right_location = 0  # 긴 거리 오른쪽

        exist_ball = FindBall().process()  # 공 찾은 값 True/False
        print("공을 찾았습니다 (T/F): ", exist_ball)

        if exist_ball == True:
            print("공이 화면에 보입니다.")
            print("공이 안 쳐진듯..")

        elif exist_ball == False:
            print("공을 찾지 못했습니다.")
            short_forward_location = 1
            if short_forward_location == 1:
                self.robo._motion.turn("LEFT", 45)
                self.robo._motion.turn("LEFT", 45)
                self.robo._motion.set_head("DOWN", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 short_forward_location에서 찾았습니다.")

                else:
                    short_left_location = 1

            if short_left_location == 1:
                print("짧은 왼쪽에 있다고 생각")

                self.robo._motion.set_head("LEFT", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 short_left_location에서 찾았습니다.")

                else:
                    short_right_location = 1

            if short_right_location == 1:
                print("짧은 오른쪽에 있다고 생각")

                self.robo._motion.set_head("RIGHT", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 short_right_location에서 찾았습니다.")

                else:
                    long_right_location = 1

            if long_right_location == 1:
                print("긴 오른쪽에 있다고 생각")

                self.robo._motion.set_head("DOWN", 80)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 long_right_location에서 찾았습니다.")

                else:
                    long_forward_location = 1

            if long_forward_location == 1:
                print("긴 가운데에 있다고 생각")

                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 long_forward_location에서 찾았습니다.")

                else:
                    long_left_location = 1

            if long_left_location == 1:
                print("긴 왼쪽에 있다고 생각")

                self.robo._motion.set_head("LEFT", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 long_left_location에서 찾았습니다.")

                else:
                    print("어라 어딨지..?")

        else:
            print("원하는 값이 반환되지 않았습니다.")

    ###################################################################################################
    # TeeShot 하기 전에 깃발 확인하고 방향 트는건데 CV랑 협의할 부분 있음.
    @classmethod
    def TeeFlagC(self):
        print("Debug TeeShot in Controller")
        time.sleep(0.1)

        flagxcenter = FlagxCenterMeasurer(img_width=640, img_height=480)
        FlagL = flagxcenter.run()

        self.robo._motion.set_head("LEFT",90)

        while FlagL[0] != 'C':

            if FlagL[0] == 'C':
                return True
            elif FlagL[0] == "L":
                self.robo._motion.turn("LEFT",3)
            elif FlagL[0] == "R":
                self.robo._motion.turn("RIGHT",3)
            else:
                print("원하는 값이 들어오지 않음.")


            
#######################################################################################################################################
    @classmethod
    def go_robo(self):
        act = self.act
        robo: Robo = Robo()
        L_right = self.L_right
        L_center = self.L_center
        L_left = self.L_left
        C_right = self.C_right
        C_center = self.C_center
        C_left = self.C_left

        canPutting = self.canPutting

        ########################################################## # test
        if act == act.TEST:
            self.robo._motion.turn("LEFT",45, 2)



            exit()
        
#############################################################################
        # 모든 것의 시작점
        if act == act.START:
            print("ACT: ", act)  # Debug
            self.act = act.SEARCH_FIRST
            
#############################################################################
        elif act == act.SEARCH_FIRST:
            print("ACT: ", act)  # Debug
            # time.sleep(0.5)
            
            # 티샷에서 공과 로봇의 위치를 찾는 함수(공과 로봇의 위치를 찾아서 L_right를 포함한 6개에 변수 중 하나를 1로 변경)
            self.check_ball_first()
            time.sleep(0.1)

            

            self.check_ball_distance()

            now_angle = self.robo._motion.y_head_angle    

            if now_angle > 69 and now_angle < 75:
                self.L_right = 1
            elif now_angle > 50 and now_angle < 63:
                self.L_center = 1
            elif now_angle < 49:
                self.L_left = 1


        
            if self.L_right == 1:  # 퍼팅 판단 return 받은걸로 모션
                print("로봇: 왼쪽, 공: 오른쪽")
                self.robo._motion.walk("FORWARD", 6)
                self.robo._motion.turn("LEFT", 3)
                self.robo._motion.walk("FORWARD", 6)
                self.robo._motion.turn("LEFT", 3)
                
                time.sleep(0.1)

                # 화면에 보이는 공을 화면상의 중심에 맞추기 위해, 로봇의 몸체를 좌우로 이동
                self.ball_feature_ball()
                time.sleep(0.1)

            elif self.L_center == 1:
                print("로봇: 왼쪽, 공: 가운데")
                self.robo._motion.walk("FORWARD", 5)
                self.robo._motion.turn("LEFT", 3)
                time.sleep(0.1)

                # 화면에 보이는 공을 화면상의 중심에 맞추기 위해, 로봇의 몸체를 좌우로 이동
                self.ball_feature_ball()
                time.sleep(0.1)

            elif self.L_left == 1:
                print("로봇: 왼쪽, 공: 왼쪽")
                self.robo._motion.walk("FORWARD", 1)
                time.sleep(0.1)

                # 화면에 보이는 공을 화면상의 중심에 맞추기 위해, 로봇의 몸체를 좌우로 이동
                self.ball_feature_ball()
                time.sleep(0.1)

            elif self.C_center == 1:
                print("로봇: 가운데, 공: 가운데")
                self.robo._motion.walk_side("LEFT", 6) # 공을 발로 차는걸 예방하기 위해서 왼쪽으로 먼저 이동.
                time.sleep(0.5)
                self.robo._motion.turn("RIGHT", 20, 4) # 90도 회전
                time.sleep(0.8)
                self.robo._motion.walk_side("LEFT", 2)
                time.sleep(0.5)
                
                self.ball_feature_ball()
                time.sleep(1)

            elif self.C_right == 1:
                print("로봇: 가운데, 공: 오른쪽")
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.5)
                self.robo._motion.walk_side("RIGHT", 4)

                # 이 밑 부분은 확인을 통해서 바꿔야 함. (C_left랑 똑같이 하면 될듯..?)
                self.robo._motion.turn("RIGHT", 20, 2)
                time.sleep(0.8)
                self.robo._motion.walk_side("LEFT", 3)
                time.sleep(0.5)
                self.robo._motion.turn("RIGHT", 20) 
                time.sleep(0.8)
                self.robo._motion.turn("RIGHT", 10)
                time.sleep(0.8)

                self.ball_feature_ball()
                time.sleep(1)

            elif self.C_left == 1:
                print("로봇: 가운데, 공: 왼쪽")

                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.5)
                self.robo._motion.walk_side("LEFT", 10)

                # 이 밑 부분은 확인을 통해서 바꿔야 함.
                self.robo._motion.turn("RIGHT", 20, 2)
                time.sleep(0.8)
                self.robo._motion.walk_side("LEFT", 3)
                time.sleep(0.5)
                self.robo._motion.turn("RIGHT", 20, 2)
                time.sleep(0.8)
                self.robo._motion.walk_side("RIGHT")

                self.ball_feature_ball()
                time.sleep(1)

            else:
                print("원하는 값이 안 옴")
                time.sleep(1)

            # +======================== 공을 화면의 y축 기준으로 중심에 맞추는 부분(우진이가 추가) ================================+
            ballycenter = BallyCenterMeasurer(img_width=640, img_height=480)
            ball_y_angle = ["N"]  # 공을 못 찾았을 때 반환하는 값
            correctAngle = 0
            putting_angle = 20
            putting_angle_error = 4
            dist_Process = DistMeasurer()

            while correctAngle != 1:
                # 이미 x축 기준으로 센터이므로, y축 기준으로 어디에 있는지 판별
                ball_y_angle = ballycenter.process()
                time.sleep(0.2)
                if ball_y_angle[0] == "C":
                    print("ball_y_angle: ", ball_y_angle[0])
                    print("중앙에 왔습니다.")
                    correctAngle = 1
                    break

                elif ball_y_angle[0] == "D" or ball_y_angle[0] == "U":
                    
                    # 아래로 1도씩 움직이기
                    recent_will_angle = 3
                    while True:
                        self.ball_feature_ball()
                        before_ball_y_angle = copy.copy(ball_y_angle[0])
                        ball_y_angle = ballycenter.process()
                        time.sleep(0.2)
                        print("ball_y: ", ball_y_angle[0])

                        if before_ball_y_angle != ball_y_angle[0]:  # 이전에 고개를 돌렸던 값과 현재 고개를 돌릴 값이 일치하면 3도 말고 1도씩만 돌리게 만듬
                            recent_will_angle = 2

                        if ball_y_angle[0] == "U":
                            self.robo._motion.set_head_small("UP", recent_will_angle)

                        elif ball_y_angle[0] == "D":
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                        
                        elif ball_y_angle[0] == "C":
                            correctAngle = 1
                            print("중앙에 왔습니다.")
                        
                            # 공 센터 맞추면 해당 각도 저장
                            ball_angle = self.robo._motion.y_head_angle
                            print("공 찾아서 각도 저장함")

                            robot_ball_angle = ball_angle - 7.6

                            # print("dist:",dist)
                            print("robot_ball_angle", robot_ball_angle)
                            print("======================")
                            time.sleep(0.1)

                            if robot_ball_angle > (putting_angle - putting_angle_error) and robot_ball_angle < (putting_angle + putting_angle_error):
                                print("퍼팅하겠습니다.")
                                break

                            elif robot_ball_angle < (putting_angle - putting_angle_error):
                                print("뒤로 가겠습니다.")
                                self.robo._motion.walk("BACKWARD", 1)

                            elif robot_ball_angle > (putting_angle + putting_angle_error):
                                print("앞으로 가겠습니다.")
                                self.robo._motion.walk("FORWARD", 1)

                            else:
                                print("T샷 C_left 오류")
            time.sleep(0.1)
            if self.L_left == 1:
                self.robo._motion.turn("RIGHT",10)
            self.robo._motion.hit_the_ball("LEFT")
            # +================================== 여기까지 추가 ================================================+
            time.sleep(0.1)
            if self.L_left == 1 or self.C_left == 1:
                self.robo._motion.turn("LEFT",45)
                self.robo._motion.turn("LEFT",20)
                self.robo._motion.turn("LEFT",10)
                print("L_LEFT일 떄 T샷이후 깃발 방향으로 턴")
            elif self.L_right == 1 or self.C_right == 1:
                self.robo._motion.turn("LEFT",45)
                self.robo._motion.turn("LEFT",20)
                self.robo._motion.turn("LEFT",20)
            else:
                self.robo._motion.turn("LEFT", 45, 2)   # 티샷 끝나고 깃발 찾기 위해 턴
                print("왼쪽으로 90도 회전")

            self.act = act.SEARCH_FLAG
                
#############################################################################
        elif act == act.SEARCH_FLAG:
            print("Act:", act)  # Debug
            shot_way = "N" # 오류 방지를 위한 shot_way 정의 (shot_way가 N이면 아직 공을 찾지 않았다는 의미)
            cnt = 1

            while(True):

                self.robo._motion.set_head("DOWN", 90)
                time.sleep(0.2)
                
                self.check_flag()   # 깃발 찾기
                if self.flag_stop == True:
                    return
                
                self.check_flag_distance() # 깃발 센터 맞추기
                self.putting_robot_turn() # 깃발이랑 로봇 몸이 일직선이 되게 만들기
                self.check_flag_distance() # 깃발 센터 맞추기

                time.sleep(0.2)
                if self.flag_stop:
                    angle = abs(self.flag_angle_y - 8.6)  # angle 값 수정
                    self.check_angle = abs(self.flag_angle_y - 8.6)  # art.check 부분에서 깃발 거리값을 쓰기 위한 변수
                else:
                    angle = abs(self.robo._motion.y_head_angle - 8.6)  # angle 값 수정
                    self.check_angle = abs(self.robo._motion.y_head_angle - 8.6)  # art.check 부분에서 깃발 거리값을 쓰기 위한 변수
                    
                distflag = DistMeasurer().display_distance(angle) # 깃발 거리값
                flag_angle = self.robo._motion.x_head_angle
                print("flag distance: ", end="")
                print(distflag)
                print("flag angle: ", end="")
                print(angle)
                
                # 깃발 거리를 측정하고 프로그램 종료
                # exit()

    #############################################################################
                # ACT: SEARCH_BALL
                print("Act: SEARCH_BALL")  # Debug
                time.sleep(0.1)
                
                # 공이 로봇 화면에서 공이 중심에 있을 수 있도록 로봇의 고개를 돌려 x, y를 맞춤
                # 만약 공이 안 잡히고, shot_way가 N이면 앞으로 걷고, 다시 깃발부터 찾기
                # 만약 공이 안 잡히고, shot_way가 R이나 L이면 hit_will_angle을 90으로 설정하고, 티샷파트로 넘어감
                self.check_ball_distance()
                
                if self.ball_stop == True:
                    return

                time.sleep(0.2)

                ball_angle = self.robo._motion.x_head_angle
                angle = abs(self.robo._motion.y_head_angle - 7.6)  # angle 값 수정
                distball = DistMeasurer().display_distance(angle) # 공 거리값
                print("ball distance: ", end="") 
                print(distball)

                time.sleep(0.2)

                # 공 거리 구하고 끝내고 싶으면
                # exit()
                # self.ball_feature_ball()
                
    #############################################################################
                print("Act: SEARCH_PUTTING_LOCATION")  # Debug

                # 공의 거리 구할 때 여기를 exit하면 공의 거리를 출력하고 멈춤
                # exit()

                print("ball_angle: ", end="")
                print(ball_angle)
                print("flag_angle: ", end="")
                print(flag_angle)

                if ball_angle >= flag_angle:   # ball angle이 더 크면 오른쪽
                    real_angle = ball_angle - flag_angle  
                    shot_way = "R" # 공이 오른쪽에 있으니 오른쪽으로
                    print("show_way = R")
                else:  # ball angle이 더 작으면 왼쪽
                    real_angle = ball_angle - flag_angle  
                    shot_way = "L" # 공이 왼쪽에 있으니 왼쪽으로
                    print("shot_wat = L")

                print("Real angle: ", end="")  # 값 확인
                print(real_angle)
                print("distflag: ", distflag)

                solver = HitPointer(distflag, distball, real_angle, 7)
                hit_dist, hit_angle, hit_will_anlge, ball_is_flag_back, flag_ball_dis = solver.solve()
                print("가야하는 거리: ", hit_dist)
                print("돌아야하는 각도", hit_angle)
                print("공앞에서 돌아야하는 각도", hit_will_anlge)
                print("공이 깃발 뒤에 있는지 없는지 (T/F): ", ball_is_flag_back)
                print("공과 깃발 사이의 거리(cm): ", flag_ball_dis)

                # 홀컵과 공의 거리의 차를 구해서 홀인 체크 파트로 넘어가는 부분
                if abs(flag_ball_dis) <= 10:
                    self.act = act.CHECK
                    return


                hit_angle = int(hit_angle)
                self.find_best_actions(hit_angle, shot_way)

                if (hit_dist < 15):
                    hit_will_go = hit_dist // 3
                    hit_will_go = int(hit_will_go)
                    self.robo._motion.walk("FORWARD", hit_will_go)

                    self.find_best_actions(hit_will_anlge, shot_way)
                    print("퍼팅 지점과 매우 가까움")
                    print("퍼팅할 준비를 하겠습니다.")
                    break

                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                #self.robo._motion.set_head("UPDOWN_CENTER")
                
                # 퍼팅 지점으로 이동하고 나서, 공과의 거리가 너무 가까워서 로봇 발로 공을 치는 문제 발생 -> 아예 퍼팅 지점 이동 전 옆으로 이동
                if shot_way == "L":
                    self.robo._motion.walk_side("RIGHT", 3)
                else:
                    self.robo._motion.walk_side("LEFT", 3)

                hit_dist = int(hit_dist)

                # self.robo._motion.walk("FORWARD", will_goto_ball, 3.0)  # 퍼팅 지점까지 걸어가기

                if cnt == 1:
                    will_goto_ball = hit_dist // 5
                    print("퍼팅 지점까지 이동")
                    self.robo._motion.turn("RIGHT", 45, 2)

                    self.robo._motion.walk_side("LEFT", will_goto_ball) # 퍼팅 지점까지 옆으로 가기

                    self.robo._motion.turn("LEFT",45, 2)
                    cnt += 1
                else:
                    will_goto_ball = hit_dist // 4
                    self.robo._motion.walk("FORWARD", will_goto_ball, 3.0) # 퍼팅 지점까지 걸어가기
                    print("퍼팅 지점까지 이동")

            time.sleep(0.1)
            
            # +======================== 퍼팅 보정하는 부분(공이 가운데 올 때까지 로봇을 움직여 x,y 조절) ==============================================+
            print("퍼팅 보정을 시작하겠습니다.")

            ballycenter = BallyCenterMeasurer(img_width=640, img_height=480)
            ball_y_angle = ["N"]  # 공을 못 찾았을 때 반환하는 값
            correctAngle = 0
            putting_angle = 20
            putting_angle_error = 4
            
            self.robo._motion.set_head("LEFTRIGHT_CENTER")
            while correctAngle != 1:

                # 퍼팅 위치까지 가고, 공이 가운데, 오른쪽, 왼쪽 중 어디에 있는지 확인해서 로봇을 옆으로(왼쪽, 오른쪽) 움직이는 모션
                self.ball_feature_ball()
                
                # 이미 x축 기준으로 센터이므로, y축 기준으로 어디에 있는지 판별
                ball_y_angle = ballycenter.process()
                time.sleep(0.2)
                if ball_y_angle[0] == "C":
                    print("ball_y_angle: ", ball_y_angle[0])
                    print("중앙에 왔습니다.")
                    correctAngle = 1
                    break

                elif ball_y_angle[0] == "D" or ball_y_angle[0] == "U":
                    
                    # 아래로 1도씩 움직이기
                    recent_will_angle = 3
                    while True:
                        self.ball_feature_ball()
                        before_ball_y_angle = copy.copy(ball_y_angle[0])
                        ball_y_angle = ballycenter.process()
                        time.sleep(0.2)
                        print("ball_y: ", ball_y_angle[0])

                        if before_ball_y_angle != ball_y_angle[0]:  # 이전에 고개를 돌렸던 값과 현재 고개를 돌릴 값이 일치하면 3도 말고 1도씩만 돌리게 만듬
                            recent_will_angle = 2

                        if ball_y_angle[0] == "U":
                            self.robo._motion.set_head_small("UP", recent_will_angle)

                        elif ball_y_angle[0] == "D":
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                        
                        elif ball_y_angle[0] == "C":
                            correctAngle = 1
                            print("중앙에 왔습니다.")
                        
                            # 공 센터 맞추면 해당 각도 저장
                            ball_angle = self.robo._motion.y_head_angle
                            print("공 찾아서 각도 저장함")

                            # dist = dist_Process.display_distance(abs(ball_angle - 11.6))
                            robot_ball_angle = ball_angle - 7.6

                            # print("dist:",dist)
                            print("robot_ball_angle", robot_ball_angle)
                            print("======================")
                            time.sleep(0.1)

                            if robot_ball_angle > (putting_angle - putting_angle_error) and robot_ball_angle < (putting_angle + putting_angle_error):
                                print("보정완료")
                                
                                if shot_way == "R":
                                    self.robo._motion.set_head("DOWN", 45)
                                    time.sleep(0.1)
                                    self.robo._motion.set_head("LEFT", 75)
                                    time.sleep(0.3)
                                    

                                else:
                                    self.robo._motion.set_head("DOWN", 45)
                                    time.sleep(0.1)
                                    self.robo._motion.set_head("RIGHT", 75)
                                    time.sleep(0.3)

                                check_angle_fbr = PuttingFlagxCenterMeasurer().run()

                                while check_angle_fbr != "C":
                                    check_angle_fbr = PuttingFlagxCenterMeasurer().run()
                                    print("마지막 퍼팅 깃발 좌우 확인: ",check_angle_fbr)
                                    if check_angle_fbr == "R":
                                        self.robo._motion.turn("RIGHT", 3)
            
                                    if check_angle_fbr == "L":
                                        self.robo._motion.turn("LEFT", 3)

                                    if check_angle_fbr == "N" and shot_way == "R":
                                        self.robo._motion.turn("LEFT", 3)

                                    if check_angle_fbr == "N" and shot_way == "L":
                                        self.robo._motion.turn("RIGHT", 3)


                                break

                            elif robot_ball_angle < (putting_angle - putting_angle_error):
                                print("뒤로 가겠습니다.")
                                self.robo._motion.walk("BACKWARD", 1)

                            elif robot_ball_angle > (putting_angle + putting_angle_error):
                                print("앞으로 가겠습니다.")
                                self.robo._motion.walk("FORWARD", 1)

                            else:
                                print("T샷 C_left 오류")


            # ========================================== 퍼팅 보정하는 부분의 끝 ==================================================
            
            print("퍼팅하겠습니다")
            print("퍼팅할 당시의 거리: ", flag_ball_dis)

            # if shot_way == "R":
            #     self.robo._motion.set_head("LEFT", 90)

            # else:
            #     self.robo._motion.set_head("RIGHT", 90)

            # flagxcenter = FlagxCenterMeasurer(img_width=640, img_height=480)

            # for i in range(3):
            #     flag_x_angle = flagxcenter.run()
            #     print(flag_x_angle)
            #     if flag_x_angle[0] == "R":
            #         self.robo._motion.turn("RIGHT", 5)
                    
            #     if flag_x_angle[0] == "L":
            #         self.robo._motion.turn("LEFT", 5)
            #     if flag_x_angle[0] == "C":
            #         print("중앙")
            #         break

            self.robo._motion.hit_the_ball("LEFT", dist=flag_ball_dis)
            time.sleep(6)


            if shot_way == 'R':

                self.robo._motion.turn("LEFT", 45, 2)   # 퍼팅 끝나고 깃발 찾기 위해 턴
                print("왼쪽으로 90도")


            else:
                self.robo._motion.turn("RIGHT", 45, 2)   # 퍼팅 끝나고 깃발 찾기 위해 턴
                print("오른쪽으로 90도")

                
#############################################################################
        elif act == act.CHECK:  # 홀인했는지 확인
            print("Act:", act)  # Debug
            
            # self.check_flag()
            # self.check_flag_distance()

            # if self.flag_stop:
            #     angle = abs(self.flag_angle_y - 8.6)  # angle 값 수정
            # else:
            #     angle = abs(self.robo._motion.y_head_angle - 8.6)  # angle 값 수정
            
            distflag = DistMeasurer().display_distance(self.check_angle) # 깃발 거리값
            check_flag_goto = distflag // 5
            check_flag_goto = int(check_flag_goto)
            self.robo._motion.walk("FORWARD", check_flag_goto)  # 퍼팅 지점까지 걸어가기
                                

            self.robo._motion.set_head("LEFTRIGHT_CENTER")
            time.sleep(0.2)
            self.robo._motion.set_head("DOWN", 45)
            time.sleep(0.2)

            # goal_detector = GoalDetect(0)
            # is_goal = goal_detector.run() # 골이 들어갔는지 판단
            # print("홀인 유무 (T/F): ", is_goal)

            # if is_goal == 'N':
            #     self.robo._motion.set_head("DOWN", 45)
            #     time.sleep(0.1)

            #     goal_detector = GoalDetect(0)
            #     is_goal = goal_detector.run() # 골이 들어갔는지 판단
            #     print("홀인 유무 (T/F): ", is_goal)
            
            
            # 깃발과 공 사이의 각도가 2도 이하일 때 골로 인식하게끔
            
            is_goal = GoalDetect().process()
            #print("홀인 체크하기 위한 깃발과 공 찾기")
            #self.check_flag()
            #self.check_flag_distance()
            #if self.flag_stop:
            #    tmp_flag_x = self.flag_angle_x
            #    tmp_flag_y = self.flag_angle_y
            #else:
            #    tmp_flag_x = self.robo._motion.x_head_angle
            #    tmp_flag_y = self.robo._motion.y_head_angle
                
            #self.check_ball_distance()
            #if self.ball_stop:
            #    tmp_ball_x = self.ball_angle_x
            #    tmp_ball_y = self.ball_angle_y
            #else:
            #    tmp_ball_x = self.robo._motion.x_head_angle
            #    tmp_ball_y = self.robo._motion.y_head_angle
                
            #print("tmp_flag_x: ", tmp_flag_x)
            #print("tmp_flag_y: ", tmp_flag_y)
            #print("tmp_ball_x: ", tmp_ball_x)
            #print("tmp_ball_y: ", tmp_ball_y)
            
            #if abs(tmp_flag_x - tmp_ball_x) <= 12 and abs(tmp_flag_y - tmp_ball_y) <= 12:
            #    is_goal = True
            

            
            print("홀인 유무 (T/F): ", is_goal)
            

            if is_goal == True:
                self.act = act.EXIT
            else:
                self.act = act.SEARCH_FLAG
                
#############################################################################
        elif act == act.EXIT:
            print("Act:", act)  # Debug

            self.robo._motion.ceremony("goal")   # 세레머니
            time.sleep(1)
            
            exit()
            
#############################################################################
        else:
            print("!!!!!!!!여기로 빠지면 큰일!!!!!!!!")

        return False