from buildhat import Motor

mouth_r = Motor('A')
mouth_l = Motor('B')

mouth_r.run_to_position(0)
mouth_l.run_to_position(0)

def move_mouth (position, speed=100):
    mouth_l.run_to_position(position * -1, speed, blocking=False) #반대 방향으로(역방향) 회전
    mouth_r.run_to_position(position, speed, blocking=False) #진행 방향으로(순방향) 회전

