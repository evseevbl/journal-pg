import psycopg2



class JournalBase(object):
    def __init__(self, code, dbw):
        self.code = code
        self.dbw = dbw
        pass


    def __del__(self):
        print(self.code, ' gonna close conn')
        self.dbw.disconnect()



class JournalClient(JournalBase):
    def __init__(self, code, dbw):
        super().__init__(code, dbw)


    def get_students_by_squad_code(self, squad: str):
        return self.dbw.query(
            "SELECT st.id, st.first_name, st.middle_name, st.last_name, st.squad_id \
            FROM students st \
            JOIN squads sq ON st.squad_id=sq.id \
            WHERE sq.code = %s",
            (squad,)
        )


    def get_squads(self):
        return self.dbw.query(
            "SELECT id, code, name FROM squads",
            ()
        )


    def get_subjects(self):
        return self.dbw.query(
            "SELECT id, short, name FROM subjects",
            ()
        )


    def get_marks_by_student(self, ID):
        return self.dbw.query(
            "SELECT id, val, date, subject_id, student_id FROM marks WHERE student_id = %s",
            (ID,)
        )


    def get_subject_name(self, ID):
        ret = self.dbw.query(
            "SELECT name, short FROM subjects WHERE id = %s",
            (ID,)
        )
        if len(ret) != 0:
            return ret[0]
        else:
            return ["", ""]


    def save_mark(self, mark):
        self.dbw.query(
            "INSERT INTO marks (student_id, teacher_id, subject_id, val, date) VALUES (%s, %s, %s, %s, %s)",
            (mark.student_id, 1, mark.subject_id, mark.val, mark.date)
        )


    def delete_mark(self, mark):
        self.dbw.query(
            "DELETE FROM marks WHERE student_id = %s AND subject_id = %s AND date = %s",
            (mark.student_id, mark.subject_id, mark.date)
        )


    def get_marks_by_squad_id(self, squad_id):
        return self.dbw.query(
            "SELECT m.id, m.val, m.date, m.subject_id, m.student_id "
            "FROM marks m "
            "JOIN students s ON m.student_id = s.id "
            "WHERE s.squad_id = %s",
            (squad_id,)
        )


    def get_marks_by_subject_squad(self, subj_ID, squad_ID):
        return self.dbw.query(
            "SELECT m.id, m.val, m.date, m.subject_id, m.student_id "
            "FROM marks m "
            "JOIN students s ON m.student_id = s.id "
            "WHERE m.subject_id = %s AND s.squad_id = %s",
            (subj_ID, squad_ID)
        )


    def get_student_by_id(self, ID):
        return self.dbw.query(
            "SELECT id, first_name, middle_name, last_name, squad_id"
            "   FROM students"
            "   WHERE id = %s",
            (ID,)
        )


    def get_penalties_by_student_id(self, ID):
        return self.dbw.query(
            "SELECT penalties.id, type, pt.name, comment, student_id, teacher_id, date "
            "   FROM penalties"
            "   JOIN penalty_types pt on penalties.type = pt.id"
            "   WHERE student_id = %s"
            "   ORDER BY penalties.date DESC",
            (ID,)
        )


    def get_duties_by_student_id(self, ID):
        return self.dbw.query(
            "SELECT d.id, type, dt.name, comment, student_id, date,"
            "   CASE WHEN d.mark IS NULL THEN '-' ELSE cast(d.mark AS VARCHAR(100)) END"
            "   FROM duties d"
            "   JOIN duty_types dt on d.type = dt.id"
            "   WHERE student_id = %s"
            "   ORDER BY d.date DESC",
            (ID,)
        )


    def get_penalty_types(self):
        return self.dbw.query(
            "SELECT id, name "
            "   FROM penalty_types"
            "   WHERE NOT penalty_types.good",
            ()
        )


    def get_promotion_types(self):
        return self.dbw.query(
            "SELECT id, name "
            "   FROM penalty_types"
            "   WHERE penalty_types.good",
            ()
        )


    def get_duty_types(self):
        return self.dbw.query(
            "SELECT id, name"
            "   FROM duty_types",
            ()
        )


    def get_good_cnt(self, ID):
        return self.dbw.query(
            "SELECT count(p.id)"
            "   FROM penalties p"
            "   JOIN penalty_types pt on p.type = pt.id"
            "   WHERE student_id = %s"
            "   AND pt.good",
            (ID,)
        )[0][0]


    def get_bad_cnt(self, ID):
        return self.dbw.query(
            "SELECT count(p.id)"
            "   FROM penalties p"
            "   JOIN penalty_types pt on p.type = pt.id"
            "   WHERE student_id = %s"
            "   AND NOT pt.good",
            (ID,)
        )[0][0]


    # ToDo teacher_id
    def add_penalty(self, penalty_type, comment, student_ID, teacher_ID, date):
        args = (penalty_type, comment, student_ID, teacher_ID, date)
        self.dbw.query(
            "INSERT INTO penalties (type, comment, student_id, teacher_id, date)"
            "   VALUES (%s, %s, %s, %s, %s)",
            args
        )
        pass


    def add_duty(self, duty_type, comment, student_ID, date, mark):
        args = (duty_type, comment, student_ID, date, mark)
        self.dbw.query(
            "INSERT INTO duties (type, comment, student_id, date, mark)"
            "   VALUES (%s, %s, %s, %s, %s)",
            args
        )
        pass


    def get_average_marks(self, student_id):
        return self.dbw.query(
            "SELECT s.short, avg(m.val)"
            "   FROM subjects s"
            "   JOIN marks m ON s.id = m.subject_id"
            "   JOIN students st ON m.student_id = st.id"
            "   WHERE student_id = %s"
            "   GROUP BY s.short",
            (student_id,)
        )


    def get_all_events(self):
        return self.dbw.query(
            "SELECT id, name, date FROM events"
            "   ORDER BY date DESC",
            [[]]
        )


    def get_all_events_without_student(self, student_id):
        return self.dbw.query(
            "SELECT e.id, e.name, e.date"
            "   FROM events e"
            "   WHERE e.id NOT IN "
            "("
            "SELECT e.id"
            "   FROM events e"
            "   JOIN event_participants ep ON e.id = ep.event_id"
            "   WHERE ep.student_id = %s"
            ")"
            "   GROUP BY e.id",
            (student_id,)

        )


    def add_event(self, date, name):
        self.dbw.query(
            "INSERT INTO EVENTS (date, name)"
            "VALUES (%s, %s)",
            (date, name)
        )


    def add_event_participant(self, event_id, student_id):
        self.dbw.query(
            "INSERT INTO event_participants (event_id, student_id)"
            "VALUES (%s, %s)",
            (event_id, student_id)
        )


    def get_events_by_student_id(self, student_id):
        return self.dbw.query(
            "SELECT e.id, e.name, e.date"
            "   FROM events e"
            "   JOIN event_participants ep ON e.id = ep.event_id"
            "   WHERE ep.student_id = %s",
            (student_id,)
        )



class DBWrapper(object):
    def __init__(self,
                 db_name='journal',
                 user='boris',
                 password='boris',
                 host='localhost',
                 port='5432'):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cur = None
        print('init db with id =', id(self))


    def connect(self):
        self.conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port)
        self.cur = self.conn.cursor()


    def disconnect(self):
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()


    def query(self, query, args):
        self.cur.execute(query, args)
        try:
            ret = self.cur.fetchall()
        except psycopg2.ProgrammingError as e:
            print(e)
            ret = None
        self.conn.commit()
        return ret


    def query_list(self, ls):
        for elem in ls:
            self.cur.execute(elem[0], elem[1])
        self.conn.commit()



class Mark(object):
    def __init__(self, ls):
        self.id = ls[0]
        self.val = ls[1]
        self.date = ls[2]
        self.subject_id = ls[3]
        self.student_id = ls[4]


    def __str__(self):
        return f'id={self.id}, val={self.val}, date={self.date}, subj={self.subject_id}, student={self.student_id}'



class Student(object):
    def __init__(self, ls):
        self.id = ls[0]
        self.first = ls[1]
        self.middle = ls[2]
        self.last = ls[3]
        self.squad_id = ls[4]


    def __str__(self):
        return f'{self.last} {self.first[0]}. {self.middle[0]}.'



class MarksTable(object):
    def __init__(self):
        pass



class Penalty(object):
    def __init__(self, ls):
        self.id = ls[0]
        self.type = ls[1]
        self.name = ls[2]
        self.comment = ls[3]
        self.student = ls[4]
        self.teacher = ls[5]
        self.date = ls[6]



class Duty(object):
    def __init__(self, ls):
        self.id = ls[0]
        self.type = ls[1]
        self.name = ls[2]
        self.comment = ls[3]
        self.student = ls[4]
        # self.teacher = ls[5]
        self.date = ls[5]
        self.mark = ls[6]



class Event(object):
    def __init__(self, ls):
        self.id = ls[0]
        self.name = ls[1]
        self.date = ls[2]
