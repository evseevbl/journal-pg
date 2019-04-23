from fbs_runtime.application_context import ApplicationContext
from PyQt5.QtWidgets import QMainWindow
from .app.marks_ui import MarksUI

import sys



class JournalApplicationContext(ApplicationContext):
    def run(self):
        window = QMainWindow()
        _ = MarksUI(window)

        window.show()
        version = self.build_settings['version']
        window.setWindowTitle("Электронный журнал, версия " + version)

        return self.app.exec_()



if __name__ == '__main__':
    ctx = JournalApplicationContext()
    exit_code = ctx.run()
    sys.exit(exit_code)
