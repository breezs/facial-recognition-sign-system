from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

from utils import connectMySQL

class SummaryController:
    def __init__(self, view):
        self.database = connectMySQL()
        self.cursor = self.database.cursor()
        self.view = view
        self.up_signdata()


    def up_signdata(self):
        week_dict = {1 : "星期一", 2: "星期二", 3: "星期三", 4: "星期四",5: "星期五"}
        sql = """select person_id, user_name, gender,class_name, work, date, weekday, time ,signed from person_sign where signed = 1"""
        self.cursor.execute(sql)
        self.database.commit()
        sign_infos = self.cursor.fetchall()
        sign_infos=list(map(list, sign_infos))
        for i, sign_info in enumerate(sign_infos):
            for j in range(9):
                if (j == 2):
                    sign_info[j] = "男" if sign_info[j] else "女"
                if(j == 5):
                    sign_info[j]=sign_info[j].strftime('%Y-%m-%d')
                if(j == 6):
                    sign_info[j] = week_dict.get(sign_info[j])
                if (j == 8):
                    sign_info[j] = "是" if sign_info[j] else "否"
                item = QTableWidgetItem(str(sign_info[j]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
                self.view.tableView.setItem(i, j, item)