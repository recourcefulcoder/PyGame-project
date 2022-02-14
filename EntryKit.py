import sys
import sqlite3
import json
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLineEdit, QApplication)
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPalette, QBrush


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
        self.initUi()

    def initUi(self):
        self.setFixedSize(600, 300)
        self.setWindowIcon(QIcon("data/images/icon.png"))
        self.instruction_btn.setIcon(QIcon("data/images/question.jpg"))
        self.greeting_label.setText(f"Здравствуй, {self.username}!")


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

            self.add_progress_info(self.login_val.text())

            self.parent.status_label.setText("Успешная регистрация!")
            self.parent.status_label.setStyleSheet('border-style: solid; border-width:'
                                                   ' 1px; border-color: green;')
        except sqlite3.IntegrityError:
            self.parent.status_label.setText('Пользователь с указанными данными уже существует')
            self.parent.status_label.setStyleSheet('border-style: solid; border-width:'
                                                   ' 1px; border-color: red;')

        self.con.commit()

        self.close()

    def add_progress_info(self, username):
        with open(f"data/progress/{username}.txt", mode='w', encoding="utf-8") as infofile:
            data = {
                "level_num": 1,
                "checkpoint": (0, [16, 24]),
                "has_shield": False,
                "has_detector": False,
                "destroyed_towers": []
            }
            writedata = json.dumps(data)
            infofile.write(writedata)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HelloWindow()
    win.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
