import unittest
import math
from db import Database
from db.Tables import School, Account, Student, Faculty, Course, Section, Rating
from processors import CollaborativeFilter
import itertools

__author__ = 'Josh'


class CollaborativeFilterTest(unittest.TestCase):
    def setUp(self):
        self.db = Database.Database(engine="sqlite://", name="", folder="")
        self.cf = CollaborativeFilter.CollaborativeFilter(self.db, "rating")
        db = self.db
        with db.scope as sesh:
            school = School(name="Georgia Institute of Technology", abbreviation="gatech")
            user = Account(username="josh", email_address="me@web.com", password_hash="hash",
                       password_salt="the saltiest")
            other = Account(username="bob", email_address="you@web.com", password_hash="hash",
                            password_salt="the saltiest")
            student = Student(school=school, account=user)
            user2 = Account(username="j", email_address="u@web.com", password_hash="hash",
                            password_salt="the saltiest")
            student2 = Student(school=school, account=user2)
            teacher = Faculty(school=school, account=other)
            sesh.add_all([school, user, other, student, user2, student2, teacher])
            courses = [Course(name="course"+str(i), abbreviation="CS"+str(i), school=school) for i in range(5)]
            sesh.add_all(courses)
            sections = [Section(professor=teacher, course=c, year=2015, semester=2) for c in courses]
            sesh.add_all(sections)
            ratings = [Rating(rating=i, section=pair[1], student=pair[0])for i, pair in enumerate(itertools.product([student, student2], sections))]
            sesh.add_all(ratings)

    def test_rss(self):
        with self.db.scope as sesh:
            student = sesh.query(Student).join(Account).filter(Account.username == "josh").one()
            self.assertEqual(math.sqrt(30), self.cf.rating_root_sum_squared(student.uid))

    def test_similarity(self):

        self.cf.course_similarity("josh", "j")

def tests():
    return unittest.TestLoader().loadTestsFromTestCase(CollaborativeFilterTest)

if __name__ == "__main__":
    unittest.main()
