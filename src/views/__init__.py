import functools
import sys

from PyQt5.QtGui import QIcon

sys.path.append(r"../")

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QTextEdit,QStackedWidget,  QSizePolicy)
from PyQt5.QtCore import QTranslator, QLocale
from qfluentwidgets import Pivot, setTheme, Theme, SegmentedWidget, FluentIcon, FluentTranslator

from views.DetectView import DetectView
from views.LoginView import LoginView
from views.SummaryView import SummaryView
from config import Config
class SegmentedWidgets(QWidget):

    def __init__(self,login_view, detect_view, summary_view):
        super().__init__()
        # setTheme(Theme.DARK)
        self.setStyleSheet("""
            SegmentedWidgets{background: white}
            PushButton{
                font: 20px 'Segoe UI';
            }
        """)
        self.resize(1390,837)
        self.setWindowTitle('人脸识别签到系统')
        self.setWindowIcon(QIcon(":/images/logo.png"))

        # 导航tab
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        # add items to pivot
        self.addSubView(login_view, 'loginview', '主页')
        self.addSubView(detect_view, 'detectview', '人脸检测')
        self.addSubView(summary_view, 'summaryview', '签到记录')

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(login_view)
        self.pivot.setCurrentItem(login_view.objectName())

    def addSubView(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            # 三种方式实现回调函数传递参数
            # onClick=lambda: self.onclicked(widget),
            # onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
            onClick = functools.partial(self.onclicked,widget)
            # onClick=self.onclicked
        )

    # functools.partial也可以实现传参数
    def onclicked(self, widget):
        # 让索引永远保存为第一个，不能跳转路由
        # 设置当前的widget
        if(Config.Allowed == False):
            # 获取第0个widget，保持为主页
            widget = self.stackedWidget.widget(0)
            self.stackedWidget.setCurrentWidget(widget)
            self.pivot.setCurrentItem(widget.objectName())
        else:
            # 获取到当前路由名字
            self.stackedWidget.setCurrentWidget(widget)
            self.pivot.setCurrentItem(widget.objectName())
    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())


class AppView(SegmentedWidgets):
    def __init__(self) -> object:
        self.login_view = LoginView()
        # loginview.show()
        self.detect_view = DetectView()
        self.summary_view = SummaryView()
        super().__init__(self.login_view,  self.detect_view, self.summary_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    view = AppView()
    view.show()
    sys.exit(app.exec_())
