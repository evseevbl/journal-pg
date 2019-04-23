from PyQt5.QtWidgets import (
    QWidget,
    QInputDialog,
)


class MarkEdit(QWidget):
    def __init__(self):
        super().__init__()

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Введите оценку', 'Оценка:')
        return text, ok
