from contextlib import contextmanager
import functools
import sqlalchemy
from . import Tables


__author__ = 'Josh'


class Database:
    def __init__(self, engine='sqlite:///', name='ClassRank.db', folder='data'):
        self.account = Tables.Account
        self.student = Tables.Student
        self.rating = Tables.Rating
        self.course = Tables.Course
        self.section = Tables.Section
        self.faculty = Tables.Faculty
        self.school = Tables.School

        self.engine = sqlalchemy.create_engine(engine + folder + "/" + name)
        self.base = Tables.Base
        self.metadata = self.base.metadata
        self.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = None

    @property
    @contextmanager
    def scope(self):
        """
        The sort of general magical sessionmanager for the database scope, allows a very
        clean usage with `with Database.scope as session:` do things
        :return: a session object
        """
        session = self.Session()
        self.session = session
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            self.session = None

    def query_rating(self, user, course, attr): #get a test for this
        return self.session.query(self.rating).join(self.section).\
            filter(self.rating.student == user,
                   self.section.course == course).one().__getattribute__(attr)

    def student_with_id(self, user_id):
        return self.session.query(self.student).filter(self.student.uid == user_id).one()

    def student_with_name(self, user_name):
        return self.session.query(self.account).filter(self.account.username == user_name).one().student

