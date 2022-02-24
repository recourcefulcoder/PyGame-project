import sys
import sqlite3
import os
import json
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLineEdit, QApplication,
                             QScrollArea, QLabel, QMainWindow,
                             QTableWidgetItem)
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPalette, QBrush
from GameProcess import game_process_main


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class HelloWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        uic.loadUi('ui_files/welcome_form.ui', self)
        self.authorization = False
        self.initUi()

    def initUi(self):
        self.setWindowTitle('Вход в систему')
        self.setWindowIcon(QIcon('data/images/icon.png'))

        self.label.setStyleSheet('color: "white"')
        self.log_label.setStyleSheet('color: "white"')
        self.pass_label.setStyleSheet('color: "white"')

        self.pass_val.setEchoMode(QLineEdit.Password)

        self.show_pass.setIcon(QIcon('data/images/eye.png'))
        self.show_pass.pressed.connect(lambda: self.pass_val.setEchoMode(QLineEdit.Normal))
        self.show_pass.released.connect(lambda: self.pass_val.setEchoMode(QLineEdit.Password))

        self.con = sqlite3.connect('database.sqlite')

        sImage = QImage("data/images/base.jfif").scaled(QSize(self.width(), self.height()))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        self.setFixedSize(QSize(self.width(), self.height()))
        self.enter_btn.clicked.connect(self.find_user)
        self.add_user_btn.clicked.connect(self.add_user)

    def find_user(self):
        if self.login_val.text() == '' or self.pass_val.text() == '':
            self.status_label.setText('Введите данные для входа')
            self.status_label.setStyleSheet(
                'border-style: solid; border-width: 1px; border-color: red; color: #ffb300')
            return
        self.status_label.setText('')
        self.status_label.setStyleSheet('')

        cur = self.con.cursor()

        data = cur.execute(f"SELECT * FROM users"
                           f"   WHERE nickname = '{self.login_val.text().strip()}'"
                           ).fetchone()

        if not data:
            self.status_label.setText('Пользователь не найден')
            self.status_label.setStyleSheet(
                'border-style: solid; border-width: 1px; border-color: red; color: #ffb300')
            return
        elif str(data[2]).strip() != self.pass_val.text():
            self.status_label.setText('Неверный пароль')
            self.status_label.setStyleSheet('color: #ffb300')
            return
        else:
            self.authorization = True
            self.close()

    def add_user(self):
        self.child_widget = AddUserWindow(self)
        self.child_widget.show()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() + 1 == Qt.Key_Enter:
            self.find_user()
        elif event.key() == Qt.Key_Down and self.focusWidget() == self.login_val:
            self.pass_val.setFocus()
        elif event.key() == Qt.Key_Up and self.focusWidget() == self.pass_val:
            self.login_val.setFocus()

    def closeEvent(self, event):
        if self.authorization:
            self.user_win = MainWindow(self.login_val.text())
            self.user_win.show()
            self.con.close()


class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)
        self.username = username
        self.game_continues = False
        self.screen_type = 'game'  # другой вариант - dialog. В соответствии с этим значением
        # в цикле функции game_process_main обрабатывается то или иное действие.
        self.dialog_is_going = False  # дабы включать стартовый диалог в game_process_main
        self.initUi()

    def initUi(self):
        self.setFixedSize(600, 300)
        self.setWindowIcon(QIcon("data/images/icon.png"))
        self.greeting_label.setText(f"Здравствуй, {self.username}!")
        self.instruction_btn.clicked.connect(self.show_instruction)
        self.new_game_btn.clicked.connect(self.start_game)
        self.load_game_btn.clicked.connect(self.load_game)
        self.statistics_btn.clicked.connect(self.load_stats)

    def show_instruction(self):
        self.instr_win = InstructionWindow()
        self.instr_win.show()

    def start_game(self):
        if not self.game_continues:
            self.reset_userdata()
            self.screen_type = 'dialog'
            game_process_main(self.username, self)

    def load_game(self):
        if not self.game_continues:
            self.game_continues = True
            game_process_main(self.username, self)

    def reset_userdata(self):
        with open(f"data/progress/{self.username}/info.txt", mode='w', encoding="utf-8") as infofile:
            data = {
                "level_num": 1,
                "checkpoint": (0, [16, 24]),
                "has_shield": False,
                "has_detector": False,
                "destroyed_towers": 0,
                "detonated_mines": [],
                "died_times": 0
            }
            writedata = json.dumps(data)
            infofile.write(writedata)
        with open(f"data/progress/{self.username}/map.txt", mode='w', encoding='utf-8') as mapfile:
            with open(f"data/levels/first_level.txt", mode='r', encoding='utf-8') as fir_level:
                map = fir_level.readlines()
                for elem in map:
                    mapfile.write(elem)

    def load_stats(self):
        self.action_win = StatisticsWindow()
        self.action_win.show()


class InstructionWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/instruction_win.ui", self)
        self.initUi()

    def initUi(self):
        self.setWindowIcon(QIcon("data/images/icon.png"))
        self.setFixedSize(self.width(), self.height())
        self.return_btn.clicked.connect(self.return_parent)
        self.init_child_widget()

    def init_child_widget(self):
        self.child_widget = QWidget(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(50, 50, self.width() - 100, self.height() - 100)
        self.setStyleSheet('QScrollArea {border-style: none;}')
        self.child_widget.setStyleSheet("QLabel {font-size: 12pt;}")
        self.scroll_area.setWidget(self.child_widget)

        self.child_widget.resize(self.width() - 100, 0)
        with open("data/game_instruction.txt", mode='r', encoding='utf-8') as instr:
            data = ''.join(instr.readlines())

        current_elem_ordinate = 20
        question = QLabel(data, self.child_widget)  # setting question
        question.setWordWrap(True)
        question.setFixedWidth(self.width() - 100)
        question.adjustSize()
        question.move(0, current_elem_ordinate)
        current_elem_ordinate += question.height() + 10  # setting question
        self.child_widget.resize(self.child_widget.width(), current_elem_ordinate)

    def return_parent(self):
        self.close()

    def closeEvent(self, event):
        delattr(self, 'scroll_area')
        delattr(self, 'child_widget')


class AddUserWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('ui_files/add_user.ui', self)
        self.setWindowTitle('Регистрация')
        self.setWindowIcon(QIcon('data/images/icon.png'))
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.return_btn.clicked.connect(self.return_parent)
        self.setFixedSize(QSize(self.width(), self.height()))

        self.action_btn.clicked.connect(self.add_user)

        self.pass_val.setEchoMode(QLineEdit.Password)
        self.repeat_pass.setEchoMode(QLineEdit.Password)

        self.show_pass.setIcon(QIcon('data/images/eye.png'))
        self.show_repeated_pass.setIcon(QIcon('data/images/eye.png'))

        self.show_pass.pressed.connect(lambda: self.pass_val.setEchoMode(QLineEdit.Normal))
        self.show_pass.released.connect(lambda: self.pass_val.setEchoMode(QLineEdit.Password))
        self.show_repeated_pass.pressed.connect(lambda: self.repeat_pass.setEchoMode(QLineEdit.Normal))
        self.show_repeated_pass.released.connect(lambda: self.repeat_pass.setEchoMode(QLineEdit.Password))

    def add_user(self):
        if self.login_val.text() == '' or self.pass_val.text() == '' or \
                self.repeat_pass.text() == '':
            self.status_label.setText('Введены не все данные')
            self.status_label.setStyleSheet('border-style: solid; border-width: 1px; border-color: red;')
            return
        elif self.repeat_pass.text() != self.pass_val.text():
            self.status_label.setText('Введённые пароли не совпадают')
            self.status_label.setStyleSheet('border-style: solid; border-width: 1px; border-color: red;')
            return
        self.status_label.setText('')
        self.status_label.setStyleSheet('')

        new_widget = ConfirmWindow(self)

        new_widget.show()

    def return_parent(self):
        self.parent.show()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() + 1 == Qt.Key_Enter:
            self.add_user()
        elif event.key() == Qt.Key_Down:
            if self.focusWidget() == self.login_val:
                self.pass_val.setFocus()
            elif self.focusWidget() == self.pass_val:
                self.repeat_pass.setFocus()
        elif event.key() == Qt.Key_Up:
            if self.focusWidget() == self.pass_val:
                self.login_val.setFocus()
            elif self.focusWidget() == self.repeat_pass:
                self.pass_val.setFocus()


class ConfirmWindow(QWidget):
    def __init__(self, parent):
        super(ConfirmWindow, self).__init__()
        uic.loadUi("ui_files/confirm_win.ui", self)

        self.parent = parent

        self.initUi()

    def initUi(self):
        self.setWindowIcon(QIcon("data/images/icon.png"))

        self.login_val.setText(self.parent.login_val.text().strip())
        self.pass_val.setText(self.parent.pass_val.text().strip())
        self.pass_val.setEchoMode(QLineEdit.Password)

        self.show_pass.setIcon(QIcon("data/images/eye.png"))
        self.show_pass.pressed.connect(lambda: self.pass_val.setEchoMode(QLineEdit.Normal))
        self.show_pass.released.connect(lambda: self.pass_val.setEchoMode(QLineEdit.Password))

        self.yes_btn.clicked.connect(self.add_user)
        self.no_btn.clicked.connect(self.close)

    def add_user(self):
        self.con = sqlite3.connect('database.sqlite')

        cur = self.con.cursor()

        try:
            cur.execute(
                f"INSERT INTO users(nickname, password) VALUES('{self.login_val.text()}', '{self.pass_val.text()}')"
            )
            id = cur.execute(f"SELECT id FROM users"
                             f"    WHERE nickname = '{self.login_val.text()}'"
                             ).fetchone()[0]
            cur.execute(f"INSERT INTO results(id) VALUES({id})"
                        )

            self.add_progress_info(self.login_val.text())

            self.parent.status_label.setText("Успешная регистрация!")
            self.parent.status_label.setStyleSheet('border-style: solid; border-width:'
                                                   ' 1px; border-color: green;')
        except sqlite3.IntegrityError:
            self.parent.status_label.setText('Пользователь с указанными данными уже существует')
            self.parent.status_label.setStyleSheet('border-style: solid; border-width:'
                                                   ' 1px; border-color: red;')

        self.con.commit()
        self.con.close()

        self.close()

    def add_progress_info(self, username):
        os.chdir("./data/progress")
        os.mkdir(f"{username}")
        os.chdir("../..")
        with open(f"data/progress/{username}/info.txt", mode='w', encoding="utf-8") as infofile:
            data = {
                "level_num": 1,
                "checkpoint": (0, [16, 24]),
                "has_shield": False,
                "has_detector": False,
                "destroyed_towers": 0,
                "detonated_mines": [],
                "died_times": 0
            }
            writedata = json.dumps(data)
            infofile.write(writedata)
        with open(f"data/progress/{username}/map.txt", mode='w', encoding='utf-8') as mapfile:
            with open(f"data/levels/first_level.txt", mode='r', encoding='utf-8') as fir_level:
                map = fir_level.readlines()
                for elem in map:
                    mapfile.write(elem)


class StatisticsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('ui_files/statistics.ui', self)
        self.setWindowTitle("Статистика")
        self.setWindowIcon(QIcon('data/images/icon.png'))

        self.con = sqlite3.connect("database.sqlite")
        self.cur = self.con.cursor()

        self.key = 4

        self.level1.clicked.connect(lambda: self.change_key(1))
        self.level2.clicked.connect(lambda: self.change_key(2))
        self.level3.clicked.connect(lambda: self.change_key(3))
        self.total_res.clicked.connect(lambda: self.change_key(4))

        self.data = [self.data_by_level(1), self.data_by_level(2), self.data_by_level(3), self.data_by_level(4)]

        self.return_btn.clicked.connect(self.close)
        self.show_all()

    def show_all(self):
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['никнейм', 'результат'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(self.data[self.key - 1]):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def data_by_level(self, num):
        columns = ["fir_level", "sec_level", "third_level", "total"]
        column = columns[num - 1]
        row_data = self.cur.execute(f"SELECT id, {column} FROM results"
                                    f"  WHERE {column} IS NOT NULL"
                                    ).fetchall()
        data = list()
        for elem in row_data:
            name = self.cur.execute(f"SELECT nickname FROM users"
                                    f"  WHERE id = {elem[0]}"
                                    ).fetchone()[0]
            data.append([name, elem[1]])
        data.sort(key=lambda x: (x[1], x[0]))
        return data

    def change_key(self, value):
        self.key = value
        self.show_all()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HelloWindow()
    win.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
