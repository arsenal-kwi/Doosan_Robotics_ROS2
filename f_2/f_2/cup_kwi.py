#!/usr/bin/env python3
import rclpy
import DR_init
import time
from math import *
ROBOT_ID    = "dsr01"
ROBOT_MODEL = "m0609"
ON = 1
OFF = 0

DR_init.__dsr__id    = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

# 1. 전역 리스트 정의
saved_xyz_values = []

def save_xyz_value(xyz):
    """xyz_value를 전역 리스트에 저장하는 함수"""
    global saved_xyz_values
    saved_xyz_values.append(xyz.copy())  # 리스트의 복사본을 저장하여 참조 문제 방지

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("doosan_drl_example", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        from DSR_ROBOT2 import (
            set_tool,
            set_tcp,
            set_digital_output,
            get_digital_input,
            task_compliance_ctrl,
            set_desired_force,
            check_force_condition,
            release_compliance_ctrl,
            get_current_posx,
            movej,
            movel,
            movesj,
            amovesj,
            _movesj,
            movesx,
            movec,
            # movesx,  # We won't use movesx
            set_singular_handling,
            set_velj,
            set_accj,
            set_velx,
            set_accx,
            trans,
            DR_AXIS_Z,
            DR_AXIS_Y,
            DR_FC_MOD_REL,
            DR_MV_ORI_RADIAL,
        )
        from DR_common2 import (posj, posx)

    except ImportError as e:
        node.get_logger().error(f"Doosan 라이브러리 임포트 오류: {e}")
        return


    def wait_digital_input(sig_num, desired_state=True, period=0.2):
        while rclpy.ok():
            val = get_digital_input(sig_num)
            if val == desired_state:
                break
            time.sleep(period)
            #print(f"Waiting for digital input #{sig_num} to be {desired_state}")

    def gripper_grip():
        set_digital_output(1, ON)
        set_digital_output(2, OFF)
        #node.get_logger().info("Gripper를 닫는 중...")
        rclpy.spin_once(node, timeout_sec=0.5)
        wait_digital_input(sig_num=1, desired_state=True)
        node.get_logger().info("Gripper가 닫혔습니다.")
        time.sleep(0.2)

    def gripper_release():
        set_digital_output(2, ON)
        set_digital_output(1, OFF)
        #node.get_logger().info("Gripper를 여는 중...")
        rclpy.spin_once(node, timeout_sec=0.2)
        wait_digital_input(sig_num=2, desired_state=True)
        node.get_logger().info("Gripper가 열렸습니다.")
        time.sleep(0.2)

    def gripper_measure():
        set_digital_output(1, ON)
        set_digital_output(2, OFF)
        node.get_logger().info("측정 중...")
        #rclpy.spin_once(node, timeout_sec=0.5)
        #wait_digital_input(sig_num=1, desired_state=True)
        node.get_logger().info("Gripper가 닫혔습니다.")
        time.sleep(0.3)
        
    #### 컵 하나 집기    
    def grip_cup(cup_index, last_pose = [366.998, 6.125, 194.183, 3.263, -179.907, 3.271]):
        node.get_logger().info(f"컵 집기 시작. 컵 인덱스: {cup_index}")
        gripper_release()
        time.sleep(0.2)

        decreased_height_grip = [0, 0, (-1) * CUP_STACK_GAP * cup_index, 0, 0, 0] # 컵 집는 위치
        cup_gripping_point = [a + b for a, b in zip(cup_starting_point_top, decreased_height_grip)]
        z_up_3 = [0, 0, 20, 0, 0, 0]
        cup_gripping_point_up = [a + b for a, b in zip(cup_gripping_point, z_up_3)]


        movesx([
            posx(last_pose),
            posx(cup_gripping_point_up),
            posx(cup_gripping_point)
        ], ref=0)
        
        # movel(posx(last_pose))
        # movel(posx(cup_gripping_point_up))
        # movel(posx(cup_gripping_point))

        node.get_logger().info(f"컵 집는 위치로 이동: {cup_gripping_point}")
        time.sleep(0.2)
        gripper_grip()
        z_up_11 = [0, 0, 150, 0, 0, 0]
        cup_gripping_point_above = [a + b for a, b in zip(cup_gripping_point, z_up_11)]

        return cup_gripping_point_above
    
    ######################################################################
    # 좌표 정의
    ######################################################################
    # 홈
    Global_0 = posj(0.00, 0.0, 90.0, 0.0, 90.0, 0.0)

    
    # 컵 시작 위치, 꼭대기 (11층) 집는 위치 (베이스 좌표)
    cup_starting_point_top = [405.801, 222.796, 213.67, 90.0, 180.0, 90.0]

    # 마지막 컵
    q1 = posj(24.972, 17.703, 51.714, 0.696, 111.215, -0.064) # posj 변수(관절각) q1 정의
    q2 = posj(72.144, 39.267, 81.066, -58.421, 113.432, 52.264) 
    q3 = posj(64.492, 53.062, 86.909, -61.17, 111.002, 57.534) 
    q4 = posj(64.854, 45.491, 86.917, -62.457, 114.783, 57.294)
    q5 = posj(12.297, -6.638, 86.488, -1.668, 95.022, 57.297)
    q6 = posj(-7.755, -27.73, 130.413, 34.295, -11.723, 57.332)
    q7 = posj(-0.6, -18.815, 144.142, 29.013, -38.438, 66.368)
    q8 = posj(-18.625, -25.266, 115.886, 27.88, 21.893, 66.352)
    q9 = posj(-18.553, -27.842, 125.458, 19.413, 26.208, 66.207)
    q10 = posj(-45.415, -22.36, 117.436, 28.442, 68.935, 17.352)
    going_to_grip_list = [q1, q2, q3]
    going_to_put_list= [q4, q5, q6, q7]
    going_home_list= [q8, q9, q10]

    CUP_DIAMETER = 82
    CUP_STACK_GAP = 11.5
    root3 = sqrt(3)

    # 로봇 설정
    set_singular_handling()  # or pass a parameter if needed
    set_velj(20.0)
    set_accj(20.0)
    set_velx(100.0, 60.625)
    set_accx(100.0, 50.5)

    cup_index = 0
    ###################### 시작
    #while rclpy.ok():
    put_down_up = [366.998, 6.125, 194.183, 3.263, -179.907, 3.271]

    starting_point = [580.0, -100.0, 84, 90.0, 180.0, 90.0]
    gripper_release()
    time.sleep(0.2)
    movej(Global_0)

    
    # 컵 쌓기
    for z in range(3):
        z_add = [0, 0, 94 * z, 0, 0, 0]
        z_value = [a + b for a, b in zip(starting_point, z_add)]
        for x in range(3-z):
            x_add = [((-1) * CUP_DIAMETER  * (root3 / 3) * z) + ((-1) * CUP_DIAMETER  * (root3 / 2) * x), 0, 0, 0, 0, 0]
            xz_value = [a + b for a, b in zip(z_value, x_add)]
            for y in range(1+x):
                #gripper_release()
                node.get_logger().info(f"층수: {z}, x: {x}, y: {y}")
                y_add = [0, (CUP_DIAMETER/2 * x) + ((-1) * CUP_DIAMETER  * y), 0, 0, 0, 0]
                xyz_value = [a + b for a, b in zip(xz_value, y_add)]

                # 2. 현재 xyz_value를 저장하는 함수 호출
                save_xyz_value(xyz_value)

                # 컵 하나 가져오기
                last_pose = grip_cup(cup_index, put_down_up)

                if y == 0:
                    z_up = [0, 0, 20, 0, 0, 0]
                else:
                    z_up = [0, 0, 110, 0, 0, 0]
                xyz_value_up = [a + b for a, b in zip(xyz_value, z_up)]
                movesx([
                    posx(last_pose),
                    posx(xyz_value_up),
                    posx(xyz_value)
                ], ref=0)
                
                # movel(last_pose)
                # node.get_logger().info(f"Move to: {xyz_value_up}")
                # movel(xyz_value_up)
                node.get_logger().info(f"Move to: {xyz_value}")
                # movel(xyz_value)

                put_down_up = xyz_value_up

                #while rclpy.ok():
                task_compliance_ctrl(stx=[3000, 3000, 3000, 100, 100, 100])
                set_desired_force(fd=[0, 0, -15, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
                while not check_force_condition(DR_AXIS_Z, max=3):
                    pass
                release_compliance_ctrl()

                gripper_release()
                cup_index += 1

    # 저장된 xyz_values 출력
    node.get_logger().info("저장된 xyz_values:")
    for value in saved_xyz_values:
        node.get_logger().info(f"{value}")
    
    #=====================================================================================
    # 컵 정리 알고리즘 추가
    #=====================================================================================

    def cleanup_cups():
        """저장된 xyz_values를 역순으로 불러와 컵을 원위치로 되돌리는 함수"""
        node.get_logger().info("컵 정리를 시작합니다.")
        
        # 컵을 되돌릴 위치 정의 (원래 컵을 가져온 시작 위치로 가정)
        cleanup_start_position = [580.0, -100.0, 84, 90.0, 180.0, 90.0]

        # 모든 컵을 역순으로 처리
        for idx, cup_position in enumerate(reversed(saved_xyz_values)):
            node.get_logger().info(f"컵 정리 진행 중: {idx+1}/{len(saved_xyz_values)}")
            
            # 컵 위치로 이동
            movej(posj(*cup_position))
            node.get_logger().info(f"컵 위치로 이동: {cup_position}")
            time.sleep(0.2)

            # 컵 잡기
            gripper_grip()
            time.sleep(0.2)

            # 컵을 원위치로 이동
            movej(posj(*cleanup_start_position))
            node.get_logger().info(f"컵을 원위치로 이동: {cleanup_start_position}")
            time.sleep(0.2)

            # 컵 놓기
            gripper_release()
            time.sleep(0.2)

            node.get_logger().info(f"컵 {idx+1} 정리가 완료되었습니다.")
    
    # 컵 정리 함수 호출
    cleanup_cups()

    #=====================================================================================
    # 컵 정리 끝
    #=====================================================================================

    # 마지막 컵 뒤집어서 놓기
    gripper_release()
    node.get_logger().info("마지막 컵")

    movej(q1)
    movej(q2)
    movej(q3)
    gripper_grip()
    time.sleep(0.2)

    movej(q4)
    movej(q5)
    movej(q6)
    movej(q7)
    
    task_compliance_ctrl(stx=[3000, 3000, 3000, 100, 100, 100])
    set_desired_force(fd=[0, 0, -15, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
    while not check_force_condition(DR_AXIS_Z, max=3):
        pass
    release_compliance_ctrl()

    gripper_release()
    time.sleep(0.2)

    #movej(q8)
    movej(q9)
    movej(q10)
    movej(Global_0)

    node.get_logger().info("노드 종료 중...")
    rclpy.shutdown()

if __name__ == "__main__":
    main()
