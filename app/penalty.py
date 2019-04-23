from PyQt5.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QDateEdit, QComboBox, QLineEdit
from PyQt5.QtCore import QDateTime


class PenaltyDialog(QDialog):
    def __init__(self, cb_items=[], parent=None, title="Взыскание"):
        super(PenaltyDialog, self).__init__(parent)
        self.cb_items = cb_items
        self.title = title
        layout = QVBoxLayout(self)

        # nice widget for editing the date
        self.date = QDateEdit(self)
        self.date.setCalendarPopup(True)
        self.date.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.date)

        self.cbType = QComboBox(self)
        for pair in self.cb_items:
            self.cbType.addItem(pair[1], pair[0])
        layout.addWidget(self.cbType)
        self.setWindowTitle(self.title)
        self.leComment = QLineEdit(self)
        self.leComment.setPlaceholderText("комментарий")
        layout.addWidget(self.leComment)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return self.date.dateTime()

    def showDialog(self, parent=None):
        result = self.exec_()
        date = self.dateTime()
        ind = self.cbType.currentIndex()
        comment = self.leComment.text()
        return date.date().toPyDate(), self.cb_items[ind], comment, result == QDialog.Accepted
