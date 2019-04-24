import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from app.ui.marks_ui import MarksUI
from app.ui.login import LoginDialog



def main():
    app = QApplication(sys.argv)
    cli, ok = LoginDialog().showDialog()
    if ok:
        window = QMainWindow()
        _ = MarksUI(window, cli)
        window.show()
    else:
        return
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
