import functools
import sys
import time

from PyQt5 import QtGui
from datetime import datetime, date
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, Qt, QTimer
from views.DetectView import DetectView
from PyQt5.QtGui import QImage, QPixmap, QIcon
from qfluentwidgets import StateToolTip, PushButton, setTheme, Theme, FluentIcon
from config import Config
import socket
import struct
import pickle
import cv2
import numpy as np
from utils import connectMySQL, createCustomInfoBar, \
                    createWarningInfoBar, transimage, go_api,recognize_face, qimage_to_cvimage

database = connectMySQL()

# 连接树莓派，传输数据图像
class AppModel:
    def __init__(self):
        self.client_socket = None
        self.connected = False

    def connect(self, ip, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, int(port)))
            self.connected = True
            return "连接成功"
        except Exception as e:
            return f"连接失败: {e}"

    def receiveData(self):
        try:
            data_size = struct.unpack(">L", self.client_socket.recv(4))[0]
            received_payload = b""
            remaining_size = data_size
            while remaining_size > 0:
                received_payload += self.client_socket.recv(remaining_size)
                remaining_size = data_size - len(received_payload)

            data = pickle.loads(received_payload)
            if data:
                image_data = data["image"]
                image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
                self.client_socket.sendall(b"ack")
                return image
            return None, None, None, None, None
        except Exception as e:
            return None, None, None, None, None

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.connected = False



# 多线程接受数据图像
class DataReceiverThread(QThread):
    dataReceived = pyqtSignal(list)
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.isRunning = True

    def run(self):
        while self.isRunning:
            image = self.model.receiveData()
            if image is not None:
                self.dataReceived.emit([image])

    def stop(self):
        self.isRunning = False
        self.wait()
class DetectController:
    def __init__(self, view, summary_controller):
        self.state_tooltip = None
        self.view = view
        self.summary_controller = summary_controller
        self.model = AppModel()
        self.dataReceiverThread = None
        self.view.connect_button.clicked.connect(self.connect_raspberry)
        self.view.save_button.clicked.connect(self.save_data)
        self.view.ip_input.setText(Config.IP)
        self.view.port_input.setText(Config.PORT)
        self.last_log_time = datetime.now()
        # self.view.timer = QTimer()
        # self.view.timer.timeout.connect(self.on_loading)
        # 人脸上传
        self.view.set_image_load_button.clicked.connect(self.load_image)
        #人脸识别
        self.view.stateTooltip = None
        self.view.set_vertify_button.clicked.connect(self.show_singleimage)

        # 保存签到数据
        self.view.set_sign_button.clicked.connect(self.save_sign)
    # Tcp连接到树莓派
    def connect_raspberry(self):
        ip = self.view.ip_input.text()
        port = self.view.port_input.text()
        result = self.model.connect(ip, port)
        self.view.connection_status.setText(f"连接状态: {result.split(':')[0]}")
        if result == "连接成功":
            self.view.set_vertify_button.setEnabled(True)
            QMessageBox.information(self.view, "连接状态", "连接成功！", QMessageBox.Ok)
            self.dataReceiverThread = DataReceiverThread(self.model)
            self.dataReceiverThread.dataReceived.connect(self.update_data)
            self.dataReceiverThread.start()

    def update_data(self, receivedData: list):
        image = receivedData[0]
        height, width, channel = image.shape
        bytesPerLine = 3 * width

        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        # pixmap = QPixmap.fromImage(qImg)

        # # 确定QLabel的大小
        # label_size = self.view.image_label.size()
        #
        # # 调整图像大小以填充QLabel
        # scaled_pixmap = pixmap.scaledToWidth(label_size.width(), Qt.SmoothTransformation)
        # 或者使用 scaledToHeight：
        # scaled_pixmap = pixmap.scaledToHeight(label_size.height(), Qt.SmoothTransformation)
        try:
            person_id, rec_image = recognize_face(image,width, height)
            if(person_id != "unknown"):
                self.person_id = person_id
            else:
                self.person_id = "unknown"
            scaled_pixmap = QPixmap.fromImage(QImage(rec_image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())
            self.view.image_label.setPixmap(scaled_pixmap)
            self.add_log_entry()
        except Exception  as e:
            print("显示异常：",e)

    def add_log_entry(self):
        current_time = datetime.now()
        if (current_time - self.last_log_time).total_seconds() > 10:#比如每10秒记录一次
            self.last_log_time = current_time  # 更新上次记录日志的时间
            # 获取当前日志框中的文本
            current_text = self.view.data_display.toPlainText()

            # 获取当前时间戳
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

            # 创建要添加的新日志条目
            new_log_entry = (f'[{timestamp}] Persion_ID: {list(Config.PERSON.keys())[0]} IP地址：{self.view.ip_input.text()}:{self.view.port_input.text()}')

            # 将新日志条目添加到当前文本后面
            self.view.data_display.setPlainText(current_text + new_log_entry +"\n")

    def save_data(self):
        # 获取文本编辑框中的文本
        data = self.view.data_display.toPlainText()
        # 获取当前时间戳来命名文件
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"log_{timestamp}.txt"
        # 打开文件以保存数据（这里示意保存到文件）
        with open(f'./log/{file_name}', 'w') as file:
            file.write(data)


    def load_image(self):
        # 设置仅仅选择图片类型
        # 如果没有连接则本地加载，否则在线录入
        try:
            ip = self.view.ip_input.text()
            port = self.view.port_input.text()
            result = self.model.connect(ip, port)
            # 再开一个连接窗口,并显示图片
            if result == "连接成功":
                self.dataReceiverThread = DataReceiverThread(self.model)
                self.dataReceiverThread.start()
                from views.TrainDialog import TrainDialog
                self.train_dialog = TrainDialog(self.dataReceiverThread)
                self.train_dialog.setWindowIcon(QIcon(":/images/logo.png"))
                # 这里顺序，先创建train_dialog，再有线程启动
                self.dataReceiverThread.dataReceived.connect(self.show_load_images)
        except Exception as e:
            print(e)


    # 上传人脸窗口显示照片
    def show_load_images(self, receivedData: list):
        try:
            image = receivedData[0]
            height, width, channel = image.shape
            bytesPerLine = 3 * width

            qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImg)
            # 确定QLabel的大小
            label_size = self.train_dialog.cameraLabel.size()
            # 调整图像大小以填充QLabel
            scaled_pixmap = pixmap.scaledToHeight(label_size.height(), Qt.SmoothTransformation)
            # 或者使用 scaledToHeight：
            # scaled_pixmap = pixmap.scaledToHeight(label_size.height(), Qt.SmoothTransformation)
            # 将调整大小后的图像设置到QLabel
            self.train_dialog.cameraLabel.setPixmap(scaled_pixmap)
            # self.train_dialog.cameraLabel.setPixmap(pixmap)
        except Exception as e:
            print("show_load_images_Error",e)

    def disconnectFromRaspberry(self):
        if self.dataReceiverThread:
            self.dataReceiverThread.stop()
        self.model.disconnect()

    # 树莓派采集时间
    def send_threshold_to_raspberry(self, open = 1):
        if self.model.connected:
            try:
                self.model.client_socket.sendall(f"SET_THRESHOLD:{open}".encode())
                print(f'已发送开门标志: {open}')
            except Exception as e:
                print(f'发送开门标志失败: {e}')


    def show_singleimage(self):
        try:
            # 显示采集加载信息
            self.state_tooltip = StateToolTip('正在采集与识别人脸信息', '请耐心等待哦~~', self.view)
            self.state_tooltip.move(410, 10)
            self.state_tooltip.show()
            if self.person_id == "unknown":
                image = self.view.image_label.pixmap().toImage()
                # 保存人脸图片
                image.save(r'resource/faceimage.jpg')
                if Config.MODEL == "BAIDU-AIP":
                    img = transimage(r'resource/faceimage.jpg')  # 根据路径读取一张图片,转换照片格式
                    # 上传到百度云得到person_id
                    self.person_id = go_api(img)  # 将转换了格式的图片上传到百度云
                    if self.person_id == "baidu-unknown":
                        createWarningInfoBar("请上传人脸")
                        return
            self.view.face_label.setText("人脸未检测或未匹配成功")
            if  self.person_id != "unknown":
                    if  self.person_id == [user_id for user_id in Config.PERSON][0]:  # 扫到的人脸
                        #发送开门指令给树莓派
                        self.view.face_label.setText(f"识别成功为{Config.PERSON.get(self.person_id)}，请签到！")
                        #识别成功才能点击签到按钮
                        self.view.set_sign_button.setEnabled( True )
                    else:
                        createWarningInfoBar("Warning","人脸(#`O′)未匹配成功，请重新连接匹配！" ,self.view)
        except Exception as e:
            print("异常：",e)
    # 保存数据
    def save_sign(self):
       try:
           if self.view.face_label.text() == "人脸未检测或未匹配成功":
               createWarningInfoBar("Warning", "人脸验证不通过", self.view)
               return
           if self.state_tooltip:
               self.state_tooltip.setState(True)
               self.state_tooltip = None

               # 签到完成，发送开门指令给树莓派
           self.send_threshold_to_raspberry(1)

           cur_weekday = datetime.now().weekday() + 1  # 判断周几
           cur_date = datetime.now().strftime("%Y-%m-%d")
           cur_time = datetime.now().strftime("%H:%M:%S")
           createCustomInfoBar("Save", "今天及时签到了哦！人家已经给您记录了数据", self.view)
           cursor = database.cursor()  # 获取游标
           # 判断今天是否已经签到
           cursor.execute("""select count(*) from person_sign where person_id = %s and date = %s""", [self.person_id, cur_date])
           database.commit()
           hava_exited = list(map(list,cursor.fetchall()))[0][0]
           if not hava_exited:
               sql = f"""insert into person_sign set date = %s, weekday = %s,time = %s, signed =%s, person_id = %s;"""  # 先保存数据，然后置零
               cursor.execute(sql, [cur_date, cur_weekday, cur_time,1,self.person_id])  # 执行sql语句
               database.commit()  # 提交到数据库执行
               sql = f"""update person_sign, person_info set person_sign.person_id =person_info.person_id, 
                        person_sign.gender = person_info.gender, person_sign.user_name = person_info.user_name, 
                        person_sign.class_name = person_info.class_name, person_sign.work = person_info.work 
                        where person_sign.person_id = person_info.person_id"""  # 先保存数据，然后置零
               cursor.execute(sql)  # 执行sql语句
               database.commit()  # 提交到数据库执行
               # 更新summary_sign
               self.summary_controller.up_signdata()
               print("数据库提交成功")

       except Exception as e:
           print("数据库写入失败",e)
        # 关闭连接
       finally:
            self.disconnectFromRaspberry()
            cursor.close()
            database.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = DetectView()
    controller = DetectController(view)
    view.show()
    sys.exit(app.exec_())
