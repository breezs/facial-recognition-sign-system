import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from controller import Controller
from views import AppView

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = AppView()
    controller = Controller(view)
    view.show()
    sys.exit(app.exec_())


# https://ts1.cn.mm.bing.net/th/id/R-C.515c02c150d8aaba4e8da18073da9946?rik=GRK2BpIU6vrgPQ&riu=http%3a%2f%2fp0.qhmsg.com%2ft01d745429df5532a04.jpg&ehk=sGuJH33uIqoYtCC3k06sfOnoE%2bDT7pWRf78ZKXdC9DA%3d&risl=&pid=ImgRaw&r=0
