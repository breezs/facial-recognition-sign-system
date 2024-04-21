from qfluentwidgets import InfoBarIcon, InfoBar, PushButton, setTheme, Theme, FluentIcon, InfoBarPosition, InfoBarManager
from PyQt5.QtCore import QPoint, Qt
def createErrorInfoBar(title, content, parent):
    InfoBar.error(
        title=title,
        content= content,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=-1,  # won't disappear automatically
        parent=parent
    )


def createWarningInfoBar(title, content, parent):
    InfoBar.warning(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=False,  # disable close button
        position=InfoBarPosition.TOP,
        duration=2000,
        parent=parent
    )

def createSuccessInfoBar(title, content, parent):
    # convenient class mothod
    InfoBar.success(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=False,
        position=InfoBarPosition.TOP,
        # position='Custom',   # NOTE: use custom info bar manager
        duration=2000,
        # 显示在自己上面
        parent=parent
    )

def createCustomInfoBar(title, content, parent):
    w = InfoBar.new(
        icon= FluentIcon.SAVE,
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=2000,
        parent=parent
    )
    w.setCustomBackgroundColor('white', '#202020')
