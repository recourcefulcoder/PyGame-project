import sys
import sqlite3
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

        self.pass_val.setEchoMode(QLineEdit.Password)

        self.show_pass.setIcon(QIcon('data/images/eye.png'))
        self.show_pass.pressed.connect(lambda: self.show_pass.setEchoMode(QLineEdit.Normal))
        self.show_pass.released.connect(lambda: self.show_pass.setEchoMode(QLineEdit.Password))

        self.con = sqlite3.connect('database.sqlite')

        sImage = QImage("data/images/base.jfif").scaled(QSize(self.width(), self.height()))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        self.setFixedSize(QSize(self.width(), self.height()))
        self.enter_btn.clicked.connect(self.find_user)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HelloWindow()
    win.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
