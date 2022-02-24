# from GameProcess import game_process_main
from EntryKit import *

app = QApplication(sys.argv)
win = HelloWindow()
win.show()
sys.excepthook = except_hook
sys.exit(app.exec())
