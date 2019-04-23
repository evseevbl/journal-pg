from PyQt5.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QDateEdit, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import QDateTime
from app import helpers as helpers
from copy import deepcopy as dc



class EventDialog(QDialog):
    def __init__(self, cli=None, student_id=None, parent=None):
        super(EventDialog, self).__init__(parent)

        self.cbType = QComboBox(self)

        self.cb_items = []
        self.student_id = student_id
        self.cli = cli
        self.update_items()

        layout = QVBoxLayout(self)

        self.bCreateEvent = QPushButton(self)
        self.bCreateEvent.setText("Создать мероприятие")
        self.bCreateEvent.clicked.connect(self.bCreateEvent_clicked)
        self.bCreateEvent.setFixedWidth(200)

        layout.addWidget(self.cbType)
        layout.addWidget(self.bCreateEvent)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


    def update_items(self):
        self.cbType.clear()
        cb_items = []
        items = self.cli.get_all_events_without_student(self.student_id)
        for i in items:
            cb_items.append([i[0], f'{helpers.date_str(i[2])}: {i[1]}'])
        self.cb_items = []
        self.cb_items = dc(cb_items)
        for pair in self.cb_items:
            self.cbType.addItem(pair[1], pair[0])
        pass


    def bCreateEvent_clicked(self):
        new = EventCreateDialog()
        date, name, ok = new.showDialog()
        if ok:
            self.cli.add_event(date, name)
            self.update_items()


    def showDialog(self):
        result = self.exec_()
        ind = self.cbType.currentIndex()
        if len(self.cb_items) == 0:
            return (None, None), False
        return self.cb_items[ind], result == QDialog.Accepted



class EventCreateDialog(QDialog):
    def __init__(self, parent=None):
        super(EventCreateDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        # nice widget for editing the date
        self.date = QDateEdit(self)
        self.date.setCalendarPopup(True)
        self.date.setDateTime(QDateTime.currentDateTime())

        self.leName = QLineEdit(self)
        self.leName.setPlaceholderText("название")

        layout.addWidget(self.date)
        layout.addWidget(self.leName)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


    # get current date and time from the dialog
    def dateTime(self):
        return self.date.dateTime()


    def showDialog(self):
        result = self.exec_()
        date = self.dateTime()
        name = self.leName.text()
        return date.date().toPyDate(), name, result == QDialog.Accepted
