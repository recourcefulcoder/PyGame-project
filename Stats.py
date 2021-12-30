from PyQt5.QtWidgets import QTabWidget
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

import sqlite3
import sys


class Kl(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('pgpr.ui', self)
        self.connection = sqlite3.connect("stata.db")
        self.pushButton.clicked.connect(self.vivod)
        self.pb_poisk.clicked.connect(self.poisk)
        self.parameters = {'ID': 'ID', 'Ник': 'Nick', 'LVL1': 'lvl1', 'LVL2': 'lvl2', 'LVL3': 'lvl3',
                           'Итог': 'itog', 'Время в игре': 'vrem'}
        self.comboBox.addItems(list(self.parameters.keys()))
        self.vivod()
        # self.dobav([3, 'nagibator', 3, 4, 5, 6, 7])

    def vivod(self):
        query = """SELECT * FROM st ORDER BY itog"""
        res = self.connection.cursor().execute(query).fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Ник', 'LVL-1', 'LVL-2',
                                                    'LVL-3', 'Итог', 'Время'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def dobav(self, a):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO st VALUES (?, ?, ?, ?, ?, ?,?)",
                    (a[0], a[1], a[2], a[3], a[4], a[5], a[6]))
        self.connection.commit()

    def poisk(self):
        cur = self.connection.cursor()
        parameter = self.comboBox.currentText()
        if self.textEdit.toPlainText().strip() != '':
            zapros = "Select * from st WHERE " + \
                     self.parameters[parameter] + " like '%" + self.textEdit.toPlainText() + "%'"
            result = cur.execute(zapros).fetchall()
            print(result)
            if result:
                self.tableWidget.setColumnCount(7)
                self.tableWidget.setHorizontalHeaderLabels(['ID', 'Ник', 'LVL-1', 'LVL-2',
                                                            'LVL-3', 'Итог', 'Время'])
                self.tableWidget.setRowCount(0)
                for i, row in enumerate(result):
                    self.tableWidget.setRowCount(
                        self.tableWidget.rowCount() + 1)
                    for j, elem in enumerate(row):
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem(str(elem)))
            else:
                QMessageBox.warning(self, '', "Мы такого не нашли", QMessageBox.Ok)

    def closeEvent(self, event):
        self.connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Kl()
    ex.show()
    sys.exit(app.exec())