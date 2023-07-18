from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#import argparse
import io
import time

import threading
import time
import numpy as np
import picamera
from signal import pause
from PIL import Image
from tflite_runtime.interpreter import Interpreter

class Classifier(object):

  """



  """

  def __init__(self, **kwargs):
    self._model = kwargs.get("model_file","")
    self._labelfile = kwargs.get("label_file","")
    self._threshold = kwargs.get("threshold",0.5)
    self._memory = kwargs.get("memory", 5)
    self._last_item_time = 0
    self._current_item = None
    self._last_item = None

    thread = threading.Thread(target=self.run, args=())
    thread.daemon = True
    thread.start()

  @property
  def item(self):
    return self._current_item

  @property
  def last_item(self):
    return self._last_item

  def load_labels(self,path):
    with open(path, 'r') as f:
      return {i: line.strip() for i, line in enumerate(f.readlines())}


  def set_input_tensor(self,interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


  def classify_image(self,interpreter, image, top_k=1):
    """분류 결과를 정렬한 배열을 반환합니다."""
    self.set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # 모델이 uint8 데이터로 되어 있는 경우, 이를 해독합니다.
    if output_details['dtype'] == np.uint8:
      scale, zero_point = output_details['quantization']
      output = scale * (output - zero_point)

    ordered = np.argpartition(-output, top_k)
    return [(i, output[i]) for i in ordered[:top_k]]


  def run(self):
    labels = self.load_labels(self._labelfile)    
#    print(labels)
    print(self._threshold)
    interpreter = Interpreter(self._model)
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']

    with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
      camera.start_preview(fullscreen=False, window = (100, 20, 640, 480))
      try:
        stream = io.BytesIO()
        for _ in camera.capture_continuous(
            stream, format='jpeg', use_video_port=True):
          stream.seek(0)
          image = Image.open(stream).convert('RGB').resize((width, height),
                                                         Image.ANTIALIAS)
          results = self.classify_image(interpreter, image)
          label_id, prob = results[0]
          label = labels[label_id]
          stream.seek(0)
          stream.truncate()

          if prob > self._threshold and label!=self._current_item:
            self._last_item_time = time.time()
            self._last_item = self._current_item
            self._current_item = label
            print(self._current_item,self._last_item)
          elif prob <= self._threshold and self._current_item!=None and time.time()-self._last_item_time > 5: 
            self._last_item = self._current_item
            self._current_item = None 
            print(self._current_item,self._last_item)


      finally:
        camera.stop_preview()


if __name__ == '__main__':
  classifier = Classifier(label_file="labels.txt",model_file="model.tflite",threshold=0.5)
  while True:
#    print(classifier.object,classifier.last_object)
    time.sleep(0.1) 
