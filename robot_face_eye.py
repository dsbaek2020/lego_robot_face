#라이브러리 추가
import board
from adafruit_ht16k33.matrix import Matrix8x8
from PIL import Image

#디스플레이로 데이터 전송용 통신 객체 생성
i2c = board.I2C()
#디스플레이 객체 생성
left_eye = Matrix8x8(i2c, address=0x70)
right_eye = Matrix8x8(i2c, address=0x71)

#png파일 이미지에서 눈동자 필셀 데이터 생성(Image 객체의 open함수 이용)
neutral = Image.open("neutral.png").rotate(90)
wide = Image.open("wide.png").rotate(90)
angry = Image.open("angry.png").rotate(90)
look_down = Image.open("look_down.png").rotate(90)

#눈동자 모양 표시 함수 정의
def change_eyes(left,right):
    left_eye.image(left)
    right_eye.image(right)
