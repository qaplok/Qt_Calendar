import time
import datetime
from datetime import timedelta
import warnings
import sys
import os
import calendar
import json
import pandas as pd
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtGui import QFont, QPen, QIntValidator
from PyQt5.QtCore import pyqtSignal, QThread
from numpy import byte, double
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
from PyQt5.QtWidgets import  QLineEdit,QMessageBox
from PyQt5.QtCore import pyqtSlot
import designQT_Calendar  # Это наш конвертированный файл дизайна


# python -m PyQt5.uic.pyuic -x designQT_Calendar.ui -o designQT_Calendar.py
# pyinstaller --noconfirm --onefile --windowed --icon=icon.ico QT_Calendar.py 
# pyrcc5 -o designQT_Calendar_rc.py designQT_Calendar.qrc 
# pyrcc5 resources.qrc -o resource_rc.py
# pyinstaller --noconfirm --onefile --windowed --icon "H:/Qt_Calendar/Calender.ico"  "H:/Qt_Calendar/QT_Calendar.py"

holidays = []
first_date_str = ''
flag_not_next_year = 0

class MyHeaderView(QHeaderView):
    def __init__(self, parent=None):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        
        self._font = QtGui.QFont("Times", 10, QFont.Weight.Bold)
        self._metrics = QtGui.QFontMetrics(self._font)
        self._descent = self._metrics.descent()
       
    def paintSection(self, painter, rect, index):
        data = self._get_data(index)
        painter.setPen(QPen(QtCore.Qt.blue, 4, QtCore.Qt.SolidLine))
        painter.drawRect(rect.x(), rect.y(), 282, 212)#rect.width(), rect.height())  
        #painter.drawRect(0,0,1,1)
        
        #painter.rotate(-90)
        painter.setFont(self._font)
                
        super().paintSection(painter, rect, index)
    '''
    def sizeHint(self):
        return QtCore.QSize(0, self._get_text_width())

    def _get_text_width(self):
        return max([self._metrics.boundingRect(self._get_data(i)).width() \
            for i in range(0, self.model().columnCount())])
    '''
    def _get_data(self, index):
        return self.model().headerData(index, self.orientation())
    
class CalendarApp(QtWidgets.QMainWindow, designQT_Calendar.Ui_MainWindow):
    
    #str_for_send = QtCore.pyqtSignal(str)
    def __init__(self):
        global holidays
        global flag_not_next_year
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        #self.listWidget.clear()
        self.onlyInt = QIntValidator()
        self.lineEdit.setValidator(self.onlyInt)
        #self.headerView = MyHeaderView()
        tooday_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
        y_str = tooday_date_str[:4]
        y_str_inte = int(y_str)
        y_str_next_inter = y_str_inte + 1
        y_str_next = str(y_str_next_inter)
        year_not_base= []
        year_in_base = []
        for i in range(1993, y_str_inte+1):
            try:
                with open("consultant" + str(i) + ".json", "r") as file_json:
                    jsonData = json.load(file_json)
                    holidays.extend(jsonData['holidays'])
                    self.statusbar.showMessage("Загружен календарь на " + str(i) + " год", 1000)
                    year_in_base.append(str(i))
            except:
                self.statusbar.showMessage("К сожалению календаря на " + str(i) + " год не добавили", 1000)
                year_not_base.append(str(i))
        try:
            with open("consultant" + y_str_next + ".json", "r") as file_json:
                jsonData = json.load(file_json)
                holidays.extend(jsonData['holidays'])
                self.statusbar.showMessage("Загружен календарь на " + y_str_next + " год", 1000)
                year_in_base.append(str(y_str_next))
                flag_not_next_year = 0
        except:
            self.statusbar.showMessage("К сожалению календаря на " + y_str_next + " год не добавили", 1000)
            year_not_base.append(y_str_next)
            self.listWidget.addItem("Внимание! Нет базы на следующий год - " + y_str_next)
            self.listWidget.addItem("если Вы ведете расчеты в конце текущего года, то программа не сможет учитывать выходные и праздники следующего года")
            flag_not_next_year = 1
        #self.draw_headers()
        self.dateEdit.setMinimumDate(QtCore.QDate(int(year_in_base[0]), 1, 1))
        self.dateEdit.setMaximumDate(QtCore.QDate(int(year_in_base[-1]), 12, 31))
        year_not_base_string = ",".join(str(element) for element in year_not_base)
        year_in_base_string = ",".join(str(element) for element in year_in_base)
        self.listWidget.addItem("Нет баз за года: " + year_not_base_string)
        self.listWidget.addItem("Загруженные года: " + year_in_base_string)
        mydate = datetime.datetime.now()
        #l = list(calendar.Calendar().itermonthdays(mydate.year, month)) # string with days
        
        self.dateEdit.setDate(mydate)
        self.redraw_tables()

        
        self.btnCalc.clicked.connect(self.CalcDate)
        self.dateEdit.dateChanged.connect(self.ChangeDateEdit)

    def ChangeDateEdit(self):
        dateEdit_str = self.dateEdit.date().toString('yyyy-MM-dd')
        self.redraw_tables()  
        self.draw_date(dateEdit_str, 'blue_light')

    def CalcDate(self):
        global holidays
        global first_date_str
        global flag_not_next_year
        need_days = self.lineEdit.text()
        if need_days == '':
            self.statusbar.showMessage("Попробуйте всё же ввести число дней", 3000)
        elif need_days == '0':
            self.statusbar.showMessage("Ноль - однозначно число, но считать тут нечего", 3000)
        else:
            if need_days == '1':
                self.statusbar.showMessage("Один день? Вы серьёзно? Ну ладно...", 3000)

            start_date_str = self.dateEdit.date().toString('yyyy-MM-dd')
            self.redraw_tables()  
            self.draw_date(start_date_str, 'blue_light')
            count_str = self.lineEdit.text()
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            

            # Подсчет рабочих дней
            current_date = start_date
            holiday_days = []
            working_days = 0
            
            
            #self.checkBox.setChecked(True)
            #while current_date.weekday() > 4 or current_date in holidays:
            
            
            if self.checkBox.checkState() == False:
                current_date += timedelta(days=int(count_str))
                curent_date_str = str(current_date.year) + '-' + f'{current_date.month:02}' + '-' + f'{current_date.day:02}'
                while curent_date_str in holidays:
                    holiday_days.append(curent_date_str)
                    current_date += timedelta(days=1)
                    curent_date_str = str(current_date.year) + '-' + f'{current_date.month:02}' + '-' + f'{current_date.day:02}'
            else:
                while int(count_str) > working_days:
                    current_date += timedelta(days=1)
                    curent_date_str = str(current_date.year) + '-' + f'{current_date.month:02}' + '-' + f'{current_date.day:02}'
                    if curent_date_str not in holidays:
                        working_days += 1
                    else:
                        holiday_days.append(curent_date_str)    
            self.draw_date(curent_date_str, "gray")
            y_str_cur = curent_date_str[:4]
            tooday_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
            y_str_start = tooday_date_str[:4]
            self.listWidget.clear()             
            self.listWidget.addItem(f"Конечная дата: " + curent_date_str)
            if flag_not_next_year == 1 and int(y_str_cur) > int(y_str_start):
                self.listWidget.addItem(" ")
                self.listWidget.addItem("Внимание! Конечная дата расчитана без учёта праздников и выходных следующего года и скорее всего не верна")
                self.listWidget.addItem(" ")
            self.listWidget.addItem(f"пропущенные праздники или выходные: {holiday_days}")
            # Вывод результата
            print(f"Конечная дата: " + curent_date_str)
            print(f"пропущенные праздники или выходные: {holiday_days}")

    def draw_date(self, date_str, color):
        global holidays
        global first_date_str
        y_first_str = first_date_str[:4]
        m_first_str = first_date_str[5:7]
        d_first_str = first_date_str[8:]
                   
        if color == "blue_light": color_draw = QtGui.QColor(128, 255, 128)
        if color == "gray": color_draw = QtGui.QColor(128, 128, 128)
        y_str = date_str[:4]
        m_str = date_str[5:7]
        d_str = date_str[8:]
        l = list(calendar.Calendar().itermonthdays(int(y_str), int(m_str))) # string with days

        if y_first_str == y_str:
            try:
                index = l.index(int(d_str))
                #print(f"Item {item} is at index {index}")
                if int(m_first_str) == int(m_str):
                    self.tableWidget.item(index//7, index - (index//7)*7).setBackground(color_draw)
                if int(m_first_str)+1 == int(m_str):
                    self.tableWidget_2.item(index//7, index - (index//7)*7).setBackground(color_draw)
                if int(m_first_str)+2 == int(m_str):
                    self.tableWidget_3.item(index//7, index - (index//7)*7).setBackground(color_draw)
                if int(m_first_str)+3 == int(m_str):
                    self.tableWidget_4.item(index//7, index - (index//7)*7).setBackground(color_draw)
            except ValueError:
                print("Item is not in the list")
        if y_first_str != y_str:
            try:
                index = l.index(int(d_str))
                #print(f"Item {item} is at index {index}")
                if int(m_first_str) == 10 and int(m_str)==1:
                    self.tableWidget_4.item(index//7, index - (index//7)*7).setBackground(color_draw)

                if int(m_first_str) == 11:
                    if int(m_str) == 1:
                        self.tableWidget_3.item(index//7, index - (index//7)*7).setBackground(color_draw)
                    if int(m_str) == 2:
                        self.tableWidget_4.item(index//7, index - (index//7)*7).setBackground(color_draw)

                if int(m_first_str) == 12:
                    if int(m_str) == 1:
                        self.tableWidget_2.item(index//7, index - (index//7)*7).setBackground(color_draw)
                    if int(m_str) == 2:
                        self.tableWidget_3.item(index//7, index - (index//7)*7).setBackground(color_draw)
                    if int(m_str) == 3:
                        self.tableWidget_4.item(index//7, index - (index//7)*7).setBackground(color_draw)
            except ValueError:
                print("Item is not in the list")

    def redraw_tables(self):
        global holidays
        global first_date_str
        self.tableWidget.clear()
        self.tableWidget_2.clear()
        self.tableWidget_3.clear()
        self.tableWidget_4.clear()
        self.draw_headers()
        
        mydate = datetime.datetime.now()
        
        #now_month = mydate.month
        tooday_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
        self.label.setText(tooday_date_str)
        start_date_str = self.dateEdit.date().toString('yyyy-MM-dd')
        first_date_str = start_date_str
        y_str = start_date_str[:4]
        m_str = start_date_str[5:7]
        d_str = start_date_str[8:]
        y_integ = int(y_str)
        m_integ = int(m_str)
        
        y_str_next = str(int(y_str)+1)
        y_integ_next = int(y_str_next)

        if m_integ >=10:
            self.label_8.setText(y_str + '-' + y_str_next)
        else:
            self.label_8.setText(y_str)
        

        '''with open("consultant" + y_str + ".json", "r") as file_json:
            jsonData = json.load(file_json)
            holidays = jsonData['holidays']
            self.statusbar.showMessage("Загружен календарь на " + y_str + " год", 2000)
            try:
                with open("consultant" + y_str_next + ".json", "r") as file_json:
                    jsonData = json.load(file_json)
                    holidays.extend(jsonData['holidays'])
                    self.statusbar.showMessage("Загружен календарь на " + y_str_next + " год", 2000)
            except:
                self.statusbar.showMessage("К сожалению календаря на " + y_str_next + " год не добавили", 8000)'''
        
        #print(jsonData)
        if m_integ == 10:
            month_this = list(calendar.Calendar().itermonthdays(y_integ, m_integ))
            month_next1 = list(calendar.Calendar().itermonthdays(y_integ, m_integ+1))
            month_next2 = list(calendar.Calendar().itermonthdays(y_integ, m_integ+2))
            month_next3 = list(calendar.Calendar().itermonthdays(y_integ_next, m_integ+3-12))
            self.label_3.setText(calendar.month_name[m_integ])
            self.label_4.setText(calendar.month_name[m_integ+1])
            self.label_5.setText(calendar.month_name[m_integ+2])
            self.label_6.setText(calendar.month_name[m_integ+3-12])
        elif m_integ == 11:
            month_this = list(calendar.Calendar().itermonthdays(y_integ, m_integ))
            month_next1 = list(calendar.Calendar().itermonthdays(y_integ, m_integ+1))
            month_next2 = list(calendar.Calendar().itermonthdays(y_integ_next, m_integ+2-12))
            month_next3 = list(calendar.Calendar().itermonthdays(y_integ_next, m_integ+3-12))
            self.label_3.setText(calendar.month_name[m_integ])
            self.label_4.setText(calendar.month_name[m_integ+1])
            self.label_5.setText(calendar.month_name[m_integ+2-12])
            self.label_6.setText(calendar.month_name[m_integ+3-12])
        elif m_integ == 12:
            month_this = list(calendar.Calendar().itermonthdays(y_integ, m_integ))
            month_next1 = list(calendar.Calendar().itermonthdays(y_integ_next, m_integ+1-12))
            month_next2 = list(calendar.Calendar().itermonthdays(y_integ_next, m_integ+2-12))
            month_next3 = list(calendar.Calendar().itermonthdays(y_integ_next, m_integ+3-12))
            self.label_3.setText(calendar.month_name[m_integ])
            self.label_4.setText(calendar.month_name[m_integ+1-12])
            self.label_5.setText(calendar.month_name[m_integ+2-12])
            self.label_6.setText(calendar.month_name[m_integ+3-12])
        else:
            month_this = list(calendar.Calendar().itermonthdays(y_integ, m_integ))
            month_next1 = list(calendar.Calendar().itermonthdays(y_integ, m_integ+1))
            month_next2 = list(calendar.Calendar().itermonthdays(y_integ, m_integ+2))
            month_next3 = list(calendar.Calendar().itermonthdays(y_integ, m_integ+3))
            self.label_3.setText(calendar.month_name[m_integ])
            self.label_4.setText(calendar.month_name[m_integ+1])
            self.label_5.setText(calendar.month_name[m_integ+2])
            self.label_6.setText(calendar.month_name[m_integ+3])
        #mydate.strftime("%B")
        #self.label_4.setText(mydate.strftime("%B")) # work
        
        
        for i in range (7):
            self.tableWidget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.tableWidget_2.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.tableWidget_3.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.tableWidget_4.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        #year_str = str(mydate.year)
        if len(month_this) == 35: month_addiction = 5 
        else: month_addiction = 6
        chi = 0
        for i in range (month_addiction):
            for k in range (7):
                if month_this[chi] != 0:
                    mons = int(m_str)
                    year_month_chi_str = y_str + '-' + f'{mons:02}' + '-' + f'{month_this[chi]:02}'
                    self.tableWidget.setItem(i, k, QtWidgets.QTableWidgetItem(str(month_this[chi])))
                    if year_month_chi_str in holidays:
                        self.tableWidget.item(i, k).setForeground(QtGui.QColor(255, 0, 0))
                    if year_month_chi_str == tooday_date_str:
                        self.tableWidget.item(i, k).setBackground(QtGui.QColor(0, 255, 250))
                chi += 1
        if len(month_next1) == 35: month_addiction = 5 
        else: month_addiction = 6
        chi = 0
        for i in range (month_addiction):
            for k in range (7):
                if month_next1[chi] != 0:
                    if m_integ == 12:
                        year_str = y_str_next
                        mons = int(m_str)+1-12
                    else:
                        mons = int(m_str)+1
                        year_str = y_str
                    year_month_chi_str = year_str + '-' + f'{mons:02}' + '-' + f'{month_next1[chi]:02}'   
                    self.tableWidget_2.setItem(i, k, QtWidgets.QTableWidgetItem(str(month_next1[chi])))
                    if year_month_chi_str in holidays:
                        self.tableWidget_2.item(i, k).setForeground(QtGui.QColor(255, 0, 0))
                    if year_month_chi_str == tooday_date_str:
                        self.tableWidget_2.item(i, k).setBackground(QtGui.QColor(0, 255, 250))
                chi += 1

        if len(month_next2) == 35: month_addiction = 5 
        else: month_addiction = 6
        chi = 0
        for i in range (month_addiction):
            for k in range (7):
                if month_next2[chi] != 0: 
                    if m_integ == 12 or m_integ == 11:
                        mons = int(m_str)+2-12
                        year_str = y_str_next
                    else:
                        mons = int(m_str)+2 
                        year_str = y_str
                    year_month_chi_str = year_str + '-' + f'{mons:02}' + '-' + f'{month_next2[chi]:02}'    
                    self.tableWidget_3.setItem(i, k, QtWidgets.QTableWidgetItem(str(month_next2[chi])))
                    if year_month_chi_str in holidays:
                        self.tableWidget_3.item(i, k).setForeground(QtGui.QColor(255, 0, 0))
                    if year_month_chi_str == tooday_date_str:
                        self.tableWidget_3.item(i, k).setBackground(QtGui.QColor(0, 255, 250))
                chi += 1

        if len(month_next3) == 35: month_addiction = 5 
        else: month_addiction = 6
        chi = 0
        for i in range (month_addiction):
            for k in range (7):
                if month_next3[chi] != 0:
                    if m_integ == 12 or m_integ == 11 or m_integ == 10:
                        mons = int(m_str)+3-12
                        year_str = y_str_next
                    else:
                        mons = int(m_str)+3
                        year_str = y_str
                    year_month_chi_str = year_str + '-' + f'{mons:02}' + '-' + f'{month_next3[chi]:02}'
                    self.tableWidget_4.setItem(i, k, QtWidgets.QTableWidgetItem(str(month_next3[chi])))
                    if year_month_chi_str in holidays:
                        self.tableWidget_4.item(i, k).setForeground(QtGui.QColor(255, 0, 0))
                    if year_month_chi_str == tooday_date_str:
                        self.tableWidget_4.item(i, k).setBackground(QtGui.QColor(0, 255, 250))

                chi += 1

    def draw_headers(self):
        self.tableWidget.setHorizontalHeaderLabels(["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"])
        self.tableWidget_2.setHorizontalHeaderLabels(["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"])
        self.tableWidget_3.setHorizontalHeaderLabels(["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"])
        self.tableWidget_4.setHorizontalHeaderLabels(["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"])
        
        style_blue = "::section {""background-color: lightblue; }"
        #style_red = "::section {""background-color: lightblue; }"
        self.tableWidget.horizontalHeader().setStyleSheet(style_blue)
        self.tableWidget_2.horizontalHeader().setStyleSheet(style_blue)
        self.tableWidget_3.horizontalHeader().setStyleSheet(style_blue)
        self.tableWidget_4.horizontalHeader().setStyleSheet(style_blue)
        
        #item1 = self.tableWidget.horizontalHeaderItem(5)
        #item2 = self.tableWidget.horizontalHeaderItem(6)
        self.tableWidget.horizontalHeaderItem(5).setForeground(QtGui.QColor(255, 0, 0))
        self.tableWidget.horizontalHeaderItem(6).setForeground(QtGui.QColor(255, 0, 0))
        item3 = self.tableWidget_2.horizontalHeaderItem(5)
        item4 = self.tableWidget_2.horizontalHeaderItem(6)
        item3.setForeground(QtGui.QColor(255, 0, 0))
        item4.setForeground(QtGui.QColor(255, 0, 0))
        item5 = self.tableWidget_3.horizontalHeaderItem(5)
        item6 = self.tableWidget_3.horizontalHeaderItem(6)
        item5.setForeground(QtGui.QColor(255, 0, 0))
        item6.setForeground(QtGui.QColor(255, 0, 0))
        item7 = self.tableWidget_4.horizontalHeaderItem(5)
        item8 = self.tableWidget_4.horizontalHeaderItem(6)
        item7.setForeground(QtGui.QColor(255, 0, 0))
        item8.setForeground(QtGui.QColor(255, 0, 0))
        #self.tableWidget.setHorizontalHeader(self.headerView)

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = CalendarApp()  # Создаём объект класса App
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()