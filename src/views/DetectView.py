import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QTextEdit,QStackedWidget,  QSizePolicy,QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore

from qfluentwidgets import LineEdit as QLineEdit
from qfluentwidgets import StateToolTip
from qfluentwidgets import (PrimaryPushButton, FluentIcon,ToggleButton,
                            IndeterminateProgressBar,SubtitleLabel,PillPushButton)
class DetectView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 最外层的水平布局
        hboxlayout = QHBoxLayout()
        # 最右侧的按钮以及信息显示
        rvboxlayout = QVBoxLayout()
        # 左侧的图像部分
        lvboxlayout = QVBoxLayout()
        _translate = QtCore.QCoreApplication.translate
        # 创建分组框
        connection_group = QGroupBox("TCP 连接")
        threshold_group = QGroupBox("人脸识别")
        image_group = QGroupBox("图像显示")
        load_group = QGroupBox("上传人脸")
        data_group = QGroupBox("日志操作")

        # 分组框布局
        connection_layout = QVBoxLayout()
        threshold_layout = QVBoxLayout()
        image_layout = QVBoxLayout()
        load_layout = QVBoxLayout()
        data_layout = QVBoxLayout()

        # TCP连接部分
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText(_translate("Form", "请输入您的IP地址："))
        self.port_input = QLineEdit()
        self.connect_button = PrimaryPushButton(FluentIcon.LINK,"连接")
        self.connection_status = QLabel('连接状态: 未连接')
        connection_layout.addWidget(QLabel('IP 地址:'))
        # connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(QLabel('端口号:'))
        connection_layout.addWidget(self.port_input)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.connection_status)
        connection_group.setLayout(connection_layout)

        # 阈值设置部分
        self.face_label =QLabel("人脸未检测或未匹配成功")
        self.face_label.setAlignment(Qt.AlignCenter)
        self.set_vertify_button = PrimaryPushButton(FluentIcon.UPDATE, '核对人脸')
        self.set_sign_button = PillPushButton(FluentIcon.SEND_FILL, '签到')
        self.set_vertify_button.setEnabled(False)
        self.set_sign_button.setEnabled(False)
        threshold_layout.addWidget(self.set_vertify_button)
        threshold_layout.addWidget(self.face_label)
        threshold_layout.addWidget(self.set_sign_button)
        threshold_group.setLayout(threshold_layout)

        # 图像显示部分
        self.image_label = QLabel('图像显示区域')
        self.image_label.setFixedSize(850, 650)
        self.image_label.setAlignment(Qt.AlignCenter)  # 图像居中显示
        self.image_label.setScaledContents(True)  # 图像缩放以填充整个 QLabel 区域
        image_layout.addWidget(self.image_label)
        self.image_label.setPixmap(QtGui.QPixmap(r"resource/backgroundimage.jpg"))
        image_group.setLayout(image_layout)

        # 人脸采集
        self.set_image_load_button = PrimaryPushButton(FluentIcon.ADD, '人脸录入')
        self.inProgressBar = IndeterminateProgressBar(self)
        self.inProgressBar.setPaused(True)
        load_layout.addWidget(self.set_image_load_button)
        load_layout.addWidget(self.inProgressBar)
        load_group.setLayout(load_layout)

        # 数据操作部分
        self.save_button = PrimaryPushButton(FluentIcon.SAVE,'保存日志')
        self.data_display = QTextEdit()
        data_layout.addWidget(self.save_button)
        data_layout.addWidget(QLabel('系统运行日志:'))
        data_layout.addWidget(self.data_display)
        data_group.setLayout(data_layout)


        # 添加分组框到栅格布局
        rvboxlayout.addWidget(connection_group)
        rvboxlayout.addWidget(threshold_group)
        # rvboxlayout.addWidget(interval_group)
        rvboxlayout.addWidget(load_group)
        rvboxlayout.addWidget(data_group)
        hboxlayout.addWidget(image_group)
        hboxlayout.addLayout(rvboxlayout)


        # 设置外层布局
        self.setLayout(hboxlayout)
        self.setWindowTitle('System')
        self.resize(1000, 600)  # 调整窗口初始大小


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # # Internationalization
    view = DetectView()
    view.show()
    sys.exit(app.exec_())
