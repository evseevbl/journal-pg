from PyQt5.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QDateEdit, QComboBox, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import QDateTime
from app import helpers as helpers
from copy import deepcopy as dc
from app.conn import DBParameters, JournalClient, DBWrapper
from psycopg2 import OperationalError



class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.params: DBParameters = None
        self.cli: JournalClient = None
        db_name = 'journal'
        host = 'localhost'
        port = '5432'
        user = 'boris'
        password = 'boris'

        self.leName = QLineEdit(self)
        self.leName.setText(db_name)
        self.leHost = QLineEdit(self)
        self.leHost.setText(host)
        self.lePort = QLineEdit(self)
        self.lePort.setText(port)

        self.leUser = QLineEdit(self)
        self.leUser.setText(user)
        self.lePassword = QLineEdit(self)
        self.lePassword.setText(password)

        self.bTryConnect = QPushButton(self)
        self.bTryConnect.setFixedWidth(150)
        self.bTryConnect.setText("Подключение")
        self.bTryConnect.clicked.connect(self.bTryConnect_clicked)

        self.lStatus = QLabel(self)
        self.lStatus.setText("")

        layout = QVBoxLayout(self)
        layout.addWidget(self.leName)
        layout.addWidget(self.leHost)
        layout.addWidget(self.lePort)
        layout.addWidget(self.leUser)
        layout.addWidget(self.lePassword)
        layout.addWidget(self.bTryConnect)
        layout.addWidget(self.lStatus)

        self.button_v = QDialogButtonBox(QDialogButtonBox.Ok, self)
        self.button_v.accepted.connect(self.accept)
        self.button_v.setEnabled(False)
        self.button_x = QDialogButtonBox(QDialogButtonBox.Cancel, self)
        self.button_x.rejected.connect(self.reject)
        layout.addWidget(self.button_v)
        layout.addWidget(self.button_x)
        # OK and Cancel buttons


    def bTryConnect_clicked(self):
        name = self.leName.text()
        host = self.leHost.text()
        port = self.lePort.text()
        user = self.leUser.text()
        password = self.lePassword.text()
        self.params = DBParameters(
            db_name=name,
            host=host,
            port=port,
            user=user,
            password=password,
        )

        dbw = DBWrapper(params=self.params)
        try:
            dbw.connect()
            self.cli = JournalClient("marks", dbw)
            self.lStatus.setText("Успешно")
            self.button_v.setEnabled(True)
        except OperationalError:
            self.lStatus.setText("Ошибка")
            self.button_v.setEnabled(False)
        pass


    def showDialog(self):
        result = self.exec_()
        return self.cli, result == QDialog.Accepted
