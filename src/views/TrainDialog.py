import json
import numpy as np
from PIL import Image
import time
import os
from PyQt5.QtCore import  QTimer, Qt, pyqtSignal
import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog, QRadioButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QMessageBox,  QInputDialog, QFileDialog

from qfluentwidgets import PrimaryPushButton as QPushButton
from urllib import request

from config import Config
from utils import createErrorInfoBar, qimage_to_cvimage


class TrainDialog(QDialog):
    mysignal = pyqtSignal()
    def __init__(self, dataReceiverThread):
        super().__init__()
        self.dataReceiverThread =dataReceiverThread

        self.setWindowTitle('人脸数据集收集和训练')
        self.resize(1000, 600)

        self.file_dialog = QFileDialog()
        self.file_dialog.setObjectName("file_dialog")

        self.IsHome_button = QRadioButton("实时收集", self)
        self.IsFile_button = QRadioButton("本地上传", self)
        self.IsInternet_button = QRadioButton("网络获取", self)
        self.collect_start_button = QPushButton("开始收集", self)
        self.train_run_button = QPushButton("开始训练", self)
        self.return_button = QPushButton("取消", self)
        self.cameraLabel = QLabel('camera', self)
        self.cameraLabel.resize(520, 360)
        self.cameraLabel.setAlignment(Qt.AlignCenter)

        self.h_col_style_layout = QHBoxLayout()
        self.v_col_styly_layout = QVBoxLayout()
        self.h_col_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.cap = cv2.VideoCapture()
        self.collect_time = QTimer()

        self.layout_init()
        self.button_init()
        self.slot_init()

        self.camera_init()
    def layout_init(self):
        self.h_col_style_layout.addWidget(self.IsHome_button)
        self.h_col_style_layout.addWidget(self.IsFile_button)
        self.h_col_style_layout.addWidget(self.IsInternet_button)
        self.setStyleSheet("""
            QRadioButton{
                width:300px;
                font: 20px;
        }
        """
        )
        self.h_col_style_layout.addStretch(1)

        self.h_col_layout.addWidget(self.collect_start_button)
        self.h_col_layout.addWidget(self.train_run_button)
        self.h_col_layout.addWidget(self.return_button)

        self.v_layout.addWidget(self.cameraLabel)
        self.v_layout.addLayout(self.h_col_style_layout)
        self.v_layout.addLayout(self.h_col_layout)

        self.setLayout(self.v_layout)


    # 按钮信号槽初始化
    def button_init(self):
        self.return_button.clicked.connect(self.cancel_task)
        self.collect_start_button.clicked.connect(self.get_image)
        self.train_run_button.clicked.connect(self.training_faces)

        self.IsHome_button.setChecked(True)

    # 信号槽初始化
    def slot_init(self):
        # self.collect_time.timeout.connect(self.show_camera)
        self.mysignal.connect(self.collect_signal_run)

    def camera_init(self):
        self.unregisterFlag = False

        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.count = 0
        # 打开已经识别的文件目录
        # 读取所有已经训练的本地数据库的名字

        # 获得这个人的个人ID
        self.person_id = [user_id for user_id in Config.PERSON][0]
        # 加入到本地数据集中
        with open(r"trainer/user_names.txt", 'r+') as fl:
            self.user_name_dict = eval(fl.read())
            self.person_ids = list(self.user_name_dict.keys())
        # 如果不在本地训练数据集中，则加入，否则弹出对话框
        if self.person_id not in self.person_ids:
            self.face_index = len(self.person_ids)
            # 将JSON格式的字符串写入文本文件
            self.user_name_dict[self.person_id] = self.face_index
            print('\n Initializing face capture. wait ...')
            self.unregisterFlag = True
            self.show()
        else:
            QMessageBox.warning(self, "Warnig","你的人脸信息已经上传了",QMessageBox.Ok)
            # 取消上传
            self.cancel_task()

    def cancel_task(self):
        self.collect_time.stop()
        self.close_camera()
        self.cap.release()
        self.cameraLabel.clear()
        self.close()

    def get_image(self):
      try:
          # 截取一张快照
          self.collect_result = None
          if self.IsHome_button.isChecked():
              # 断开线程
              self.dataReceiverThread.stop()
              time.sleep(1)
              # 获得此时的照片显示
              self.image = qimage_to_cvimage(self.cameraLabel.pixmap().toImage())
              # 打开文件夹
          elif self.IsFile_button.isChecked():
              self.dataReceiverThread.stop()
              time.sleep(1)
              image_file, type = self.file_dialog.getOpenFileName(self, 'Open file', 'C:\\',
                                                            'Image files (*.jpg *.gif *.png *.jpeg)')
              self.image = cv2.imread(image_file)
          elif self.IsInternet_button.isChecked():
              try:
                  self.dataReceiverThread.stop()
                  time.sleep(1)
                  image_url, ok = QInputDialog.getText(self, '请输入图片URL', '可在线获取的图片地址')
                  with request.urlopen(image_url) as f:
                      data = f.read()
                      img1 = np.frombuffer(data, np.uint8)
                      self.image = cv2.imdecode(img1, cv2.IMREAD_COLOR)
              except Exception as e:
                  createErrorInfoBar("Error","请输入正确的URL地址", self)
                  return
          self.img = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
          # pyqt显示图片逻辑
          qImg = QImage(self.img.data, self.img.shape[1], self.img.shape[0], QImage.Format_RGB888)
          pixmap = QPixmap.fromImage(qImg)
          label_size = self.cameraLabel.size()
          # 调整图像大小以填充QLabel
          scaled_pixmap = pixmap.scaledToHeight(label_size.height(), Qt.SmoothTransformation)
          # 或者使用 scaledToHeight：
          # scaled_pixmap = pixmap.scaledToHeight(label_size.height(), Qt.SmoothTransformation)
          # 将调整大小后的图像设置到QLabel
          self.cameraLabel.setPixmap(scaled_pixmap)
      except Exception as e:
          print(e)

    def collect_faces(self, image):
        try:
            # 转为灰度图片
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # 检测人脸
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x + w, y + w), (255, 0, 0), 2)
                # 保存图像,从原始照片中截取人脸尺寸
                cv2.imwrite(
                    f"trainer/faceimages/{[user_id for user_id in Config.PERSON][0]}." + str(self.face_index)
                         + '.jpg', gray[y: y + h, x: x + w])
        except Exception as e:
            print(e)

    def training_faces(self):
        try:
            self.collect_faces(self.image)
            # 人脸数据路径
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

            def getImagesAndLabels(data_path):
                imagePaths = [os.path.join(data_path, f) for f in os.listdir(data_path)]  # join函数的作用？
                faceSamples = []
                ids = []
                for imagePath in imagePaths:
                    PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
                    img_numpy = np.array(PIL_img, 'uint8')
                    id = int(os.path.split(imagePath)[-1].split(".")[1])
                    faces = detector.detectMultiScale(img_numpy)
                    for (x, y, w, h) in faces:
                        faceSamples.append(img_numpy[y:y + h, x: x + w])
                        ids.append(id)
                if len(np.unique(ids)) != len(list(self.user_name_dict.keys())):
                    raise Exception
                return faceSamples, ids

            print('Training faces. It will take a few seconds. Wait ...')
            faces, ids = getImagesAndLabels(r"trainer/faceimages")
            recognizer.train(faces, np.array(ids))

            recognizer.write(r"trainer/trainer.xml")
            print("{0} faces trained. Exiting Program".format(len(np.unique(ids))))
            # 保存训练记录到本地数据集中
            with open(r"trainer/user_names.txt", "w") as f:
                f.write(json.dumps(self.user_name_dict))

            QMessageBox.information(self, "训练消息", "训练完毕", QMessageBox.Ok)
            # 关闭相机
            self.close_camera()
        except Exception as e:
            print("训练错误",e)
            createErrorInfoBar("Error","请上传清晰正确的人脸图片",self)

    def collect_signal_run(self):
        self.collect_result = QMessageBox.information(self, '训练', '收集完成', QMessageBox.Ok)

        # 对图片的格式进行转换

    def close_camera(self):
        self.collect_time.stop()
        self.cameraLabel.clear()