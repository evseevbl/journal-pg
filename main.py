import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from app.ui.marks_ui import MarksUI



def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    _ = MarksUI(window)
    window.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
