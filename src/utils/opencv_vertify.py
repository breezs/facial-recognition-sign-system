import os

import cv2

from config import Config

recognizer = cv2.face.LBPHFaceRecognizer_create()
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
font = cv2.FONT_HERSHEY_SIMPLEX
def recognize_face(image, width, height):
    result = "unknown"  # 初始化识别失败
    if os.path.exists(r"trainer/trainer.xml"):
        recognizer.read(r"trainer/trainer.xml")
    else:
        return result, image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        if confidence < 50:  # 50%的识别置信度
            fl = open(r"trainer/user_names.txt", 'r+')
            real_dict = eval(fl.read())
            person_ids = list(real_dict.keys())
            result = person_ids[id]
            confidencestr = "{0}%".format(round(100 - confidence))
            # go_api( round(100 - confidence) , int( idnum  ) , tag  , names)

        else:
            confidencestr = "{0}%".format(round(100 - confidence))
        cv2.putText(image, result, (x + 5, y - 5), font, 1, (0, 0, 255), 2)
        # cv2.putText(image, confidencestr, (x + 5, y + h - 5), font, 1, (0, 0, 0), 1)
    return result, image