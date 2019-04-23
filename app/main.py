from PyQt5.QtWidgets import QMainWindow, QApplication
from app.ui.marks_ui import MarksUI

import sys



def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    _ = MarksUI(window)

    window.show()
    window.setWindowTitle("Электронный журнал, версия " + "ff")
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
