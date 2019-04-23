from PyQt5.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QDateEdit
from PyQt5.QtCore import QDateTime


class DateDialog(QDialog):
    def __init__(self, parent=None):
        super(DateDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        # nice widget for editing the date
        self.date = QDateEdit(self)
        self.date.setCalendarPopup(True)
        self.date.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.date)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return self.date.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = DateDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return date.date().toPyDate(), result == QDialog.Accepted
