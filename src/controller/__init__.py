
from .detect_controller import DetectController
from .login_controller import LoginController
from .summary_controller import SummaryController

class Controller:
    def __init__(self, Appview):
        self.app_view = Appview
        self.login_controller = LoginController(Appview.login_view)
        self.summary_controller = SummaryController(Appview.summary_view)
        # self.detect_controller = DetectController(Appview.detect_view)

        # 传递summary_controller用于更新表格，解决循环引用问题
        self.detect_controller = DetectController(Appview.detect_view, self.summary_controller)





