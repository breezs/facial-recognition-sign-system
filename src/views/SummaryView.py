# coding: utf-8
import sys
import datetime

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QStyleOptionViewItem, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout, \
    QHeaderView

from qfluentwidgets import TableWidget, isDarkTheme, setTheme, Theme, TableView, TableItemDelegate, setCustomStyleSheet

class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """
    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return

        if isDarkTheme():
            option.palette.setColor(QPalette.Text, Qt.white)
            option.palette.setColor(QPalette.HighlightedText, Qt.white)
        else:
            option.palette.setColor(QPalette.Text, Qt.red)
            option.palette.setColor(QPalette.HighlightedText, Qt.red)


class SummaryView(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        self.hBoxLayout = QHBoxLayout(self)
        self.tableView = TableWidget(self)

        # NOTE: use custom item delegate
        self.tableView.setItemDelegate(CustomTableItemDelegate(self.tableView))
        # select row on right-click
        self.tableView.setSelectRightClickedRow(True)

        # self.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter)  # 设置表格的水平对齐方式为居中对齐
        # self.tableView.verticalHeader().setDefaultAlignment(Qt.AlignHCenter)  # 设置表格的垂直对齐方式为居中对齐

        # enable border
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)

        self.tableView.setWordWrap(False)
        self.tableView.setRowCount(60)
        self.tableView.setColumnCount(9)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['工号','姓名', '性别', '部门', '职位', '日期','周次','时间','签到记录'])
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setSortingEnabled(True)

        self.setStyleSheet("Demo{background: rgb(255, 255, 255)} ")
        self.hBoxLayout.setContentsMargins(50, 30, 50, 30)
        self.hBoxLayout.addWidget(self.tableView)
        self.resize(735, 760)


if __name__ == "__main__":
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = SummaryView()
    w.show()
    app.exec()
