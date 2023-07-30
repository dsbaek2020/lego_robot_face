from buildhat import Motor

import board
from adafruit_ht16k33.matrix import Matrix8x8
from PIL import Image

#from classifier import Classifier
from classifier_edgetpu import Classifier

from time import sleep

#print("go....")
#print("boot robot face")

i2c = board.I2C()
left_eye = Matrix8x8(i2c, address=0x71)
right_eye = Matrix8x8(i2c, address=0x70)


neutral = Image.open("neutral.png").rotate(90)
wide = Image.open("wide.png").rotate(90)
angry = Image.open("angry.png").rotate(90)
look_down = Image.open("look_down.png").rotate(90)


mouth_r = Motor('A')
mouth_l = Motor('B')
eyebrows = Motor('C')
#print("motor initialize ok.")

faces = {
    "neutral":   {"mouth":0,   "right_eye":neutral,   "left_eye":neutral,   "eyebrows":0},
    "angry":     {"mouth":45,  "right_eye":wide,      "left_eye":wide,      "eyebrows":150},
    "happy":     {"mouth":-20, "right_eye":angry,     "left_eye":angry,     "eyebrows":-150},
    "sad":       {"mouth":-45, "right_eye":look_down, "left_eye":look_down, "eyebrows":-40}
    }

#seen_items = Classifier(label_file="labels.txt",model_file="model.tflite",threshold=0.5)
seen_items = Classifier(label_file="labels.txt",model_file="new_jinhae_girls_h_model_edgetpu.tflite",threshold=0.8)

reactions = {"game_pad"            : "sad",
             "remote_controller"   : "neutral",
             "lego_bird"           : "angry",
             "Cat"                 : "happy"}

mouth_r.run_to_position(0)
mouth_l.run_to_position(0)
eyebrows.run_to_position(0)

def set_face (face):
    change_eyes(face["right_eye"],face["left_eye"])
    move_mouth(face["mouth"])
    move_eyebrows(face["eyebrows"])

def change_eyes(left,right):
    left_eye.image(left)
    right_eye.image(right)

def move_eyebrows (position):
    current_position = eyebrows.get_aposition()
    if position < current_position:
        rotation = 'anticlockwise'
    else:
        rotation = 'clockwise'
    eyebrows.run_to_position(position, direction = rotation)


def move_mouth (position, speed=100):
    mouth_l.run_to_position(position * -1, speed, blocking=False) #반대 방향으로(역방향) 회전
    mouth_r.run_to_position(position, speed, blocking=False) #진행 방향으로(순방향) 회전


for face in faces:
  set_face(faces[face])

set_face(faces["happy"])

while True:
    sleep(1)
    if seen_items.item != seen_items.last_item:
        item = seen_items.item
        print('item=', item[0], 'probability=', round(item[1],2))
        if item in reactions.keys():
            set_face(faces[reactions[item]])
    sleep(1)

