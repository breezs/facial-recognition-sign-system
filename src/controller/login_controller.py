import sys
from datetime import datetime

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from qfluentwidgets import Dialog, BodyLabel, LineEdit

from views.DetectView import DetectView as AppView
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from config import Config
from views import AppView, LoginView

from utils import createWarningInfoBar,createErrorInfoBar,createSuccessInfoBar

from utils import connectMySQL
class LoginController:
    def __init__(self, view):
        self.view = view
        # 登录按钮
        self.view.pushButton.clicked.connect(self.login)
        self.view.pushButton_2.clicked.connect(self.sign)
        self.database = connectMySQL()
        self.cursor = self.database.cursor()
        # self.view.checkBox.stateChanged.connect(lambda: print(checkBox.isChecked()))


    def login(self):

       try:
           # 登录
           user_id = self.view.lineEdit_3.text()
           pwd = self.view.lineEdit_4.text()
           # 将密码核对
           if not user_id and not pwd:
               createWarningInfoBar("Warnninng", "请输入您的姓名和密码", self.view)
           elif not user_id and pwd:
               createWarningInfoBar("Warnninng", "请输入您的姓名", self.view)

           elif not pwd and user_id:
               createWarningInfoBar("Warnninng", "请输入您的密码", self.view)
           else:
               # 去数据库查询密码
               sql = "select user_password, user_name from person_info where person_id = %s "
               self.cursor.execute(sql, user_id)
               self.database.commit()
               user_message = list(map(list, self.cursor.fetchall()))[0]
               user_password = user_message[0]
               user_name = user_message[1]
               if user_password:
                   if (user_password == pwd):
                       Config.Allowed = True
                       Config.PERSON[user_id] = user_name
                       createSuccessInfoBar("Success", "恭喜您登录成功·", self.view)
               else:
                   createErrorInfoBar("Error", "密码错误，请核对密码", self.view)
       except Exception as e:
           print("查询错误",e)

    def sign(self):
        try:
            self.sign_dialog = Dialog("注册", "权限不够，注册请联系管理员！", self.view)
            self.sign_dialog.resize(650, 409)
            self.sign_dialog.show()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = LoginView()
    controller = LoginController(view)
    # controller.login()
    view.show()
    sys.exit(app.exec_())
