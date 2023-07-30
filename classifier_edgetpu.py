#{home}/coral/pycoral/examples 에서 
# imprinting_learning.py 파일 절차에 따라서 
#  첫번째 학습을 시키고 최초의  모델 생성 

# 그다음{home}/문서/teacher/image_training
# 에서 retrain 과정을 실행한다. 
# 참조: Image classification with google coral (code club project)

# 생성된 edgetpu 모델파일과 라벨파일을 classifier_edgetup.py (이 파일)
# 이 있는 폴더에 복사한다.  


import re
import os
import cv2
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters import common
from pycoral.adapters import classify

import threading
import time

# the TFLite converted to be used with edgetpu
modelPath = 'new_jinhae_girls_h_model_edgetpu.tflite'

# The path to labels.txt that was downloaded with your model
labelPath = 'labels.txt'

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



  def classifyImage(self,interpreter, image):
    size = common.input_size(interpreter)
    common.set_input(interpreter, cv2.resize(image, size, fx=0, fy=0,
                                             interpolation=cv2.INTER_CUBIC))
    interpreter.invoke()
    return classify.get_classes(interpreter)


  def run(self):
    # Load your model onto the TF Lite Interpreter
    interpreter = make_interpreter(modelPath)
    interpreter.allocate_tensors()
    labels = read_label_file(labelPath)

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip image so it matches the training input
        frame = cv2.flip(frame, 1)

        # Classify and display image
        results = self.classifyImage(interpreter, frame)
        label_id, prob = results[0]
        label = labels[label_id]
        
        if prob > self._threshold and label!=self._current_item:
            self._last_item_time = time.time()
            self._last_item = self._current_item
            self._current_item = label, prob
            #print(self._current_item,self._last_item)

        elif prob <= self._threshold and self._current_item!=None and time.time()-self._last_item_time > 5: 
            self._last_item = self._current_item
            self._current_item = None 
            #print(self._current_item,self._last_item)
          
        cv2.imshow('frame', frame)
        #print(f'Label: {labels[results[0].id]}, Score: {results[0].score}')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':
  classifier = Classifier(label_file="labels.txt",model_file="model_edgetpu.tflite",threshold=0.5)
  while True:
#    print(classifier.object,classifier.last_object)
    time.sleep(0.1) 
