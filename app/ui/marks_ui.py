from .marks import Ui_wMarks
from app.conn import DBWrapper, JournalClient, Mark, Student, Penalty, Duty, Event

from psycopg2 import OperationalError
from PyQt5.QtCore import QModelIndex

from app.ui.model import MyTableModel
from app.ui.mark_edit import MarkEdit
from app.ui.date import DateDialog
from app.ui.penalty import PenaltyDialog
from app.ui.event import EventDialog
from app.ui.duty import DutyDialog
from app import helpers
from datetime import datetime
from copy import deepcopy as dc



class MarksUI(object):
    def __init__(self, window):
        wm = Ui_wMarks()
        wm.setupUi(window)
        self.teacher_id = 1
        self.current_subjects = list()  # list(["ТЧиП", "ВСП", "ОГП"])
        self.current_dates = [datetime.today()]  # so that IDE provides type assistance
        self.new_dates = list()

        self.w = wm

        self.arr_student = [[]]
        self.arr_subj = [[]]
        self.arr_student_prev = [[]]
        self.arr_subj_prev = [[]]
        self.arr_penalties = [[]]
        self.arr_avg = [[]]
        self.arr_duties = [[]]
        self.arr_events = [[]]

        self.w.tMarksStudent.setHidden(True)
        self.dbw = DBWrapper()

        try:
            self.dbw.connect()
            self.cli = JournalClient("marks", self.dbw)
            # init database
            self.connect_handlers()
            self.fill_squads()

            self.current_students = []
            self.current_students_ids = []
        except OperationalError as e:
            print("no db: ", e)

        self.student_model = MyTableModel(None, self.arr_student, [], [])
        self.subj_model = MyTableModel(None, self.arr_subj, [], [])
        self.penalties_model = MyTableModel(None, self.arr_penalties, [], [])
        self.duties_model = MyTableModel(None, self.arr_duties, [], [])
        self.avg_model = MyTableModel(None, self.arr_avg, [], [])
        self.events_model = MyTableModel(None, self.arr_events, [], [])


    def connect_handlers(self):
        self.w.bMarksInputStudent.clicked.connect(self.bMarksInputStudent_clicked)
        self.w.bMarksInputSubject.clicked.connect(self.bMarksInputSubject_clicked)
        self.w.bAddDate.clicked.connect(self.bAddDate_clicked)
        self.w.cbSquad.currentIndexChanged.connect(self.cbSquad_currentIndexChanged)
        self.w.cbStudent.currentIndexChanged.connect(self.cbStudent_currentIndexChanged)
        self.w.cbSubject.currentIndexChanged.connect(self.fill_table_subject)
        self.w.tMarksStudent.clicked.connect(self.edit_mark_student)
        self.w.tMarksSubject.clicked.connect(self.edit_mark_subject)
        self.w.tabWidget.currentChanged.connect(self.tabWidget_currentChanged)
        self.w.bAddPenalty.clicked.connect(self.bAddPenalty_clicked)
        self.w.bAddPromotion.clicked.connect(self.bAddPromotion_clicked)
        self.w.bAddDuty.clicked.connect(self.bAddDuty_clicked)
        self.w.twStudentInfo.currentChanged.connect(self.twStudentInfo_currentChanged)
        self.w.bAddEvent.clicked.connect(self.bAddEvent_clicked)


    def cbStudent_currentIndexChanged(self, _):
        self.set_student_name()
        self.fill_table_student()
        self.fill_table_penalties()
        self.fill_table_duties()
        self.fill_penalty_counters()
        self.fill_table_average()
        self.fill_table_events()


    def tabWidget_currentChanged(self, _):
        ind = self.w.tabWidget.currentIndex()
        if ind == 0:
            self.fill_table_student()
        elif ind == 1:
            self.fill_table_subject(None)


    def cbSquad_currentIndexChanged(self):
        self.fill_students()
        self.fill_subjects()


    def fill_students(self):
        ID, code = self.get_current_squad()
        students = self.cli.get_students_by_squad_code(code)
        self.w.cbStudent.clear()
        for student in students:
            s = Student(student)
            txt = str(s)
            # f'{last} {first[0]}. {middle[0]}.'
            self.w.cbStudent.addItem(txt, s.id)
        pass


    def fill_squads(self):
        squads = self.cli.get_squads()
        self.w.cbSquad.clear()
        for sq in squads:
            ID, code, _ = sq
            self.w.cbSquad.addItem(code, ID)
            pass


    def fill_subjects(self):
        subjects = self.cli.get_subjects()
        self.w.cbSubject.clear()
        for s in subjects:
            ID, short, name = s
            self.w.cbSubject.addItem(short, ID)
            pass


    def get_current_student(self):
        ID = self.w.cbStudent.itemData(self.w.cbStudent.currentIndex())
        name = self.w.cbStudent.currentText()
        return ID, name


    def get_current_squad(self):
        ID = self.w.cbSquad.itemData(self.w.cbSquad.currentIndex())
        code = self.w.cbSquad.currentText()
        return ID, code


    def get_current_subject(self):
        ID = self.w.cbSubject.itemData(self.w.cbSubject.currentIndex())
        name = self.w.cbSubject.currentText()
        return ID, name


    def get_current_student_marks(self):
        ID, _ = self.get_current_student()
        marks = self.cli.get_marks_by_student(ID)
        ls = list()
        for m in marks:
            ls.append(Mark(m))
        return ls


    def get_current_subject_marks(self):
        squad_ID, _ = self.get_current_squad()
        subj_ID, _ = self.get_current_subject()
        marks = self.cli.get_marks_by_subject_squad(subj_ID, squad_ID)
        ls = list()
        for m in marks:
            ls.append(Mark(m))
        return ls


    def get_current_squad_marks(self):
        ID, _ = self.get_current_squad()
        marks = self.cli.get_marks_by_squad_id(ID)
        ls = list()
        for m in marks:
            ls.append(Mark(m))
        return ls


    def get_current_squad_students(self):
        ids = list()
        names = list()
        _, code = self.get_current_squad()
        students = self.cli.get_students_by_squad_code(code)
        for student in students:
            s = Student(student)
            txt = str(s)
            names.append(txt)
            ids.append(s.id)
        return ids, names


    def fill_table_student(self):
        marks = self.get_current_student_marks()

        self.current_subjects = self.get_all_subjects()
        self.current_dates = self.get_all_dates()
        self.arr_student = [['' + '' for _ in range(len(self.current_dates))] for _ in
                            range(len(self.current_subjects))]
        self.student_model = MyTableModel(None, self.arr_student, self.get_current_dates_str(), self.current_subjects)
        self.w.tMarksStudent.setModel(self.student_model)
        self.w.tMarksStudent.setVisible(True)
        if len(marks) == 0:
            return
        if len(self.current_dates) == 0 or len(self.current_subjects) == 0:
            return

        for i in range(len(self.current_subjects)):
            for j in range(len(self.current_dates)):
                for mark in marks:
                    # ToDo IMPORTANT fix subj_id
                    if str(mark.date) == str(self.current_dates[j]) and mark.subject_id == i + 1:
                        ind = self.get_model_index(self.student_model, i, j)
                        self.set_at_index(self.student_model, ind, mark.val)


    def fill_table_subject(self, _):
        # ID, name = self.get_current_subject()
        marks = self.get_current_subject_marks()

        self.current_students_ids, self.current_students = self.get_current_squad_students()

        self.current_dates = self.get_all_dates()
        self.arr_subj = [
            ['' + '' for _ in range(len(self.current_dates))]
            for _ in range(len(self.current_subjects))
        ]
        self.subj_model = MyTableModel(None, self.arr_subj, self.get_current_dates_str(), self.current_students)
        self.w.tMarksSubject.setModel(self.subj_model)
        self.w.tMarksSubject.setVisible(True)
        if len(marks) == 0:
            return
        if len(self.current_dates) == 0 or len(self.current_students) == 0:
            return
        for i in range(len(self.current_students)):
            for j in range(len(self.current_dates)):
                for mark in marks:
                    if str(mark.date) == str(self.current_dates[j]) and mark.student_id == self.current_students_ids[i]:
                        ind = self.get_model_index(self.subj_model, i, j)
                        self.set_at_index(self.subj_model, ind, mark.val)


    def fill_table_penalties(self):
        self.w.tPenalties.setVisible(False)
        self.w.lPenalties.setVisible(True)
        # ToDo fix
        self.penalties_model = MyTableModel(None, [[]], [], [])
        self.w.tPenalties.setModel(self.penalties_model)
        self.w.tPenalties.setVisible(False)
        ID, name = self.get_current_student()
        penalties = self.cli.get_penalties_by_student_id(ID)
        if len(penalties) == 0:
            return

        header = ("Дата", "Вид", "Комментарий")
        self.current_students_ids, self.current_students = self.get_current_squad_students()

        self.arr_penalties = []
        for penalty in penalties:
            p = Penalty(penalty)
            self.arr_penalties.append(
                (
                    helpers.date_str(p.date),
                    p.name,
                    p.comment
                )
            )

        if len(penalties) == 0:
            return
        self.penalties_model = MyTableModel(None, self.arr_penalties, header, ['', '', '', '', '', ''])
        self.w.tPenalties.setModel(self.penalties_model)
        self.w.tPenalties.setColumnWidth(0, 200)
        self.w.tPenalties.setColumnWidth(1, 200)
        self.w.tPenalties.setColumnWidth(2, self.w.tPenalties.width() - 400 - 10)
        self.w.lPenalties.setVisible(False)
        self.w.tPenalties.setVisible(True)


    def fill_table_events(self):
        self.w.tEvents.setVisible(False)
        self.w.lEvents.setVisible(True)
        # ToDo fix
        self.events_model = MyTableModel(None, [[]], [], [])
        self.w.tEvents.setModel(self.events_model)
        self.w.tEvents.setVisible(False)
        ID, name = self.get_current_student()
        events = self.cli.get_events_by_student_id(ID)
        if len(events) == 0:
            return

        header = ("Дата", "Название")
        self.arr_events = []
        for event in events:
            p = Event(event)
            self.arr_events.append(
                (
                    helpers.date_str(p.date),
                    p.name
                )
            )

        if len(events) == 0:
            return
        self.events_model = MyTableModel(None, self.arr_events, header, ['', '', '', '', '', ''])
        self.w.tEvents.setModel(self.events_model)
        self.w.tEvents.setColumnWidth(0, 200)
        self.w.tEvents.setColumnWidth(1, self.w.tEvents.width() - 200 - 10)
        self.w.lEvents.setVisible(False)
        self.w.tEvents.setVisible(True)


    def fill_table_duties(self):
        self.w.tDuties.setVisible(False)
        self.w.lDuties.setVisible(True)
        # ToDo fix
        self.duties_model = MyTableModel(None, [[]], [], [])
        self.w.tDuties.setModel(self.duties_model)
        self.w.tDuties.setVisible(False)
        ID, name = self.get_current_student()
        duties = self.cli.get_duties_by_student_id(ID)
        if len(duties) == 0:
            return

        header = ("Дата", "Вид", "Комментарий", "Оценка")
        self.current_students_ids, self.current_students = self.get_current_squad_students()

        self.arr_duties = []
        for duty in duties:
            p = Duty(duty)
            self.arr_duties.append(
                (
                    helpers.date_str(p.date),
                    p.name,
                    p.comment,
                    p.mark
                )
            )

        if len(duties) == 0:
            return
        self.duties_model = MyTableModel(None, self.arr_duties, header, ['', '', '', '', '', ''])
        self.w.tDuties.setModel(self.duties_model)
        self.w.tDuties.setColumnWidth(0, 200)
        self.w.tDuties.setColumnWidth(1, 200)
        self.w.tDuties.setColumnWidth(2, 100)
        self.w.tDuties.setColumnWidth(2, self.w.tDuties.width() - 500 - 10)
        self.w.lDuties.setVisible(False)
        self.w.tDuties.setVisible(True)


    def bAddDate_clicked(self, _):
        new_date, ok = self.get_date()
        self.new_dates.append(new_date)
        self.fill_table_student()
        self.fill_table_subject(None)


    def bMarksInputStudent_clicked(self, _):
        if self.w.tMarksStudent.isEnabled():
            self.w.tMarksStudent.setEnabled(False)
            self.w.cbStudent.setEnabled(True)
            self.w.cbSquad.setEnabled(True)
            self.w.bMarksInputStudent.setText("Ввод оценок")
            self.save_marks_student()
            # self.w.twSubject.setEnabled(True)
        else:
            self.w.tMarksStudent.setEnabled(True)
            self.w.cbStudent.setEnabled(False)
            self.w.cbSquad.setEnabled(False)
            self.w.bMarksInputStudent.setText("Сохранить")
            self.arr_student_prev = dc(self.arr_student)
            # self.w.twSubject.setEnabled(False)
        pass


    def bMarksInputSubject_clicked(self, _):
        if self.w.tMarksSubject.isEnabled():
            self.w.tMarksSubject.setEnabled(False)
            self.w.cbSubject.setEnabled(True)
            self.w.cbSquad.setEnabled(True)
            self.w.bMarksInputSubject.setText("Ввод оценок")
            self.save_marks_subject()
            # self.w.twSubject.setEnabled(True)
        else:
            self.w.tMarksSubject.setEnabled(True)
            self.w.cbSubject.setEnabled(False)
            self.w.cbSquad.setEnabled(False)
            self.w.bMarksInputSubject.setText("Сохранить")
            self.arr_subj_prev = dc(self.arr_subj)
            # self.w.twSubject.setEnabled(False)
        pass


    def get_unique_subjects(self, marks):
        subject_set = set()
        for m in marks:
            name, short = self.cli.get_subject_name(m.subject_id)
            subject_set.add(short)
        return list(subject_set)


    def edit_mark(self, model, item):
        z = QModelIndex(item)
        form = MarkEdit()
        text, ok = form.showDialog()
        if ok:
            self.set_at_index(model, z, text)


    def edit_mark_student(self, item):
        self.edit_mark(self.student_model, item)


    def edit_mark_subject(self, item):
        self.edit_mark(self.subj_model, item)


    @staticmethod
    def get_date():
        date, ok = DateDialog.getDateTime()
        return date, ok


    @staticmethod
    def get_unique_dates(marks: [Mark]) -> [datetime.date]:
        date_set = set()
        for m in marks:
            date_set.add(m.date)
        ls = list(date_set)
        ls.sort()
        return ls


    @staticmethod
    def set_at_index(model, ind, text):
        model.updateAtIndex(ind, text)
        pass


    def save_marks_student(self):
        for i in range(len(self.current_subjects)):
            for j in range(len(self.current_dates)):
                if self.arr_student_prev[i][j] != self.arr_student[i][j]:
                    noVal = False
                    try:
                        val = int(self.arr_student[i][j])
                    except ValueError:
                        val = -1
                        noVal = True
                    student_id, _ = self.get_current_student()
                    subject_id = i + 1
                    date = self.current_dates[j]
                    mark = Mark((
                        0,
                        val,
                        date,
                        subject_id,
                        student_id,
                    ))
                    if noVal:
                        self.cli.delete_mark(mark)
                    else:
                        self.cli.save_mark(mark)
                    pass


    def save_marks_subject(self):
        for i in range(len(self.current_students)):
            for j in range(len(self.current_dates)):
                if self.arr_subj_prev[i][j] != self.arr_subj[i][j]:
                    noVal = False
                    try:
                        val = int(self.arr_subj[i][j])
                    except ValueError:
                        val = -1
                        noVal = True
                    student_id = self.current_students_ids[i]
                    subj_id, _ = self.get_current_subject()
                    date = self.current_dates[j]
                    mark = Mark((
                        0,
                        val,
                        date,
                        subj_id,
                        student_id,
                    ))
                    if noVal:
                        self.cli.delete_mark(mark)
                    else:
                        self.cli.save_mark(mark)
                    pass


    @staticmethod
    def get_model_index(model, i, j):
        return model.index(0, 0).sibling(i, j)


    @staticmethod
    def get_all_subjects():
        # ToDo fix, should be taken from DB
        return ["ТЧиП", "ВСП", "ОГП"]


    def get_all_dates(self):
        self.current_dates = self.get_unique_dates(self.get_current_squad_marks())
        self.append_dates(self.new_dates)
        return self.current_dates


    def append_dates(self, dates):
        cd = dc(self.current_dates)
        for new_date in dates:
            should_add = True
            for date in self.current_dates:
                if date == new_date:
                    should_add = False
            if should_add:
                cd.append(new_date)
                cd.sort()
        self.current_dates = dc(cd)


    def get_current_dates_str(self):
        return list(map(helpers.date_str, self.current_dates))


    def set_student_name(self):
        try:
            ID, _ = self.get_current_student()
            ret = self.cli.get_student_by_id(ID)
            ret = ret[0]
            s = Student(ret)
            self.w.lFirst.setText(s.first)
            self.w.lMiddle.setText(s.middle)
            self.w.lLast.setText(s.last)
        except IndexError:
            pass


    def bAddPenalty_clicked(self):
        ID, _ = self.get_current_student()
        items = self.cli.get_penalty_types()
        date, (penalty_type, _), comment, ok = PenaltyDialog(cb_items=items).showDialog()
        if ok:
            # ToDo teacher_id
            self.cli.add_penalty(penalty_type, comment, ID, self.teacher_id, date)
            self.fill_table_penalties()
            self.fill_penalty_counters()
        pass


    def bAddPromotion_clicked(self):
        ID, _ = self.get_current_student()
        items = self.cli.get_promotion_types()
        date, (penalty_type, _), comment, ok = PenaltyDialog(cb_items=items, title="Поощрение").showDialog()
        if ok:
            # ToDo teacher_id
            self.cli.add_penalty(penalty_type, comment, ID, self.teacher_id, date)
            self.fill_table_penalties()
            self.fill_penalty_counters()
        pass


    def bAddDuty_clicked(self):
        ID, _ = self.get_current_student()
        items = self.cli.get_duty_types()
        date, (duty_type, _), comment, mark, ok = DutyDialog(cb_items=items).showDialog()
        if ok:
            # ToDo teacher_id
            self.cli.add_duty(duty_type, comment, ID, date, mark)
            self.fill_table_duties()
        pass


    def bAddEvent_clicked(self):
        student_id, _ = self.get_current_student()
        (event_id, _), ok = EventDialog(cli=self.cli, student_id=student_id).showDialog()
        if ok:
            self.cli.add_event_participant(event_id, student_id)
            self.fill_table_events()


    def fill_penalty_counters(self):
        ID, _ = self.get_current_student()
        good = self.cli.get_good_cnt(ID)
        bad = self.cli.get_bad_cnt(ID)
        self.w.lGoodCnt.setText(str(good))
        self.w.lBadCnt.setText(str(bad))
        pass


    def fill_table_average(self):
        ID, _ = self.get_current_student()
        avg = self.cli.get_average_marks(ID)
        arr = []
        for line in avg:
            name = line[0]
            val = float(line[1])
            arr.append([name, val])

        header = ("Предмет", "Средний балл")
        if len(arr) == 0:
            return

        self.avg_model = MyTableModel(None, arr, header, [])
        self.w.tAverage.setModel(self.avg_model)
        self.w.tAverage.setColumnWidth(0, 100)
        self.w.tAverage.setColumnWidth(1, 150 - 10)
        # self.w.lPenalties.setVisible(False)
        self.w.tAverage.setVisible(True)


    def fill_table_squad_average(self):
        _, code = self.get_current_squad()
        avg = self.cli.get_average_marks(code)
        arr = []
        for line in avg:
            name = line[0]
            val = float(line[1])
            arr.append([name, val])

        header = ("Предмет", "Средний балл")
        if len(arr) == 0:
            return

        self.avg_model = MyTableModel(None, arr, header, [])
        self.w.tAverage.setModel(self.avg_model)
        self.w.tAverage.setColumnWidth(0, 100)
        self.w.tAverage.setColumnWidth(1, 150 - 10)
        # self.w.lPenalties.setVisible(False)
        self.w.tAverage.setVisible(True)


    def twStudentInfo_currentChanged(self, _):
        self.fill_table_average()
        self.fill_table_duties()
