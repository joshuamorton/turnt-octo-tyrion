import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from db.Tables import School, Account, Student, Faculty, Base, Course, Section, Rating
from sqlalchemy import create_engine


__author__ = 'Josh'


class TableTest(unittest.TestCase):

    def setUp(self):
        # creates an in memory db for testing
        engine = create_engine('sqlite://')  # in memory db
        self.metadata = Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

    def build_situation(self):
        school = School(name="Georgia Institute", abbreviation="gatech")
        user = Account(username="josh", email_address="me@web.com", password_hash="hash",
                       password_salt="the saltiest")
        other = Account(username="bob", email_address="you@web.com", password_hash="hash",
                        password_salt="the saltiest")
        student = Student(school=school, account=user)
        user2 = Account(username="j", email_address="u@web.com", password_hash="hash",
                        password_salt="the saltiest")
        student2 = Student(school=school, account=user2)
        teacher = Faculty(school=school, account=other)
        del self
        return locals()

    def test_account_nulls(self):
        # makes sure that everything is not nullable
        self.session.add(Account())
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(Account(username="name", email_address="addr", password_hash="pw"))
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(Account(username="name", email_address="addr", password_salt="salt"))
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(Account(username="name", password_hash="pw", password_salt="salt"))
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(Account(email_address="addr", password_salt="salt", password_hash="pw"))
        self.assertRaises(IntegrityError, self.session.commit)

    def test_account(self):
        # you can add an account
        self.session.add(Account(username="bob", email_address="me@test.com",
                                 password_hash="secret", password_salt="table"))
        self.session.commit()
        # and it persists
        self.assertEqual("bob", self.session.query(Account).all()[0].username)

    def test_school_nulls(self):
        # makes sure that everything is not nullable
        self.session.add(School())
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(School(name="testschool"))
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(School(abbreviation="testabbr"))
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()

    def test_full_db(self):
        # builds a small test database and checks it to be sure that all basic operations
        # work as intended
        school = School(name="Georgia Institute", abbreviation="gatech")
        user = Account(username="josh", email_address="me@web.com", password_hash="hash",
                       password_salt="the saltiest")
        other = Account(username="bob", email_address="you@web.com", password_hash="hash",
                        password_salt="the saltiest")
        student = Student(school=school, account=user)
        teacher = Faculty(school=school, account=other)

        self.session.add(school)
        self.session.add(user)
        self.session.add(student)
        self.session.add(other)
        self.session.add(teacher)
        self.session.commit()

        self.assertEqual(school, school.students[0].school)
        self.assertEqual(school, school.faculty[0].school)
        self.assertEqual(user, user.student.account)
        self.assertEqual(user.student.school, other.faculty.school)

    def test_doubled_user(self):
        # a user account can be bound to both a student and faculty instance, this checks
        # that that functions correctly
        school = School(name="Georgia Institute", abbreviation="gatech")
        user = Account(username="josh", email_address="me@web.com", password_hash="hash",
                       password_salt="the saltiest")
        student = Student(school=school, account=user)
        teacher = Faculty(school=school, account=user)

        self.session.add(school)
        self.session.add(user)
        self.session.add(student)
        self.session.add(teacher)
        self.session.commit()

        self.assertEqual(student.account, teacher.account)

    def test_school_uniqueConstraint(self):
        # unique constraints work for school names
        school = School(name="Georgia Institute", abbreviation="gatech")
        other = School(name="Georgia Institute", abbreviation="gate")
        third = School(name="blargh", abbreviation="gatech")

        self.session.add(school)
        self.session.commit()
        self.session.add(other)
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(third)
        self.assertRaises(IntegrityError, self.session.commit)

    def test_account_uniqueConstraint(self):
        # unique constraint works on email and username
        user = Account(password_hash='a', password_salt="b", username="n", email_address="addr")
        other = Account(password_hash='a', password_salt="b", username="o", email_address="addr")
        third = Account(password_hash='a', password_salt="b", username="n", email_address="a")

        self.session.add(user)
        self.session.commit()
        self.session.add(other)
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.session.add(third)
        self.assertRaises(IntegrityError, self.session.commit)

    def test_teacher_ratings(self):
        objects = self.build_situation()
        course = Course(name="mine", abbreviation="m", school=objects["school"])
        course2 = Course(name="other", abbreviation="o", school=objects["school"])
        section = Section(professor=objects["teacher"], course=course, semester=1, year=2014)
        section2 = Section(professor=objects["teacher"], course=course2, semester=2, year=2014)
        rating = Rating(student=objects["student"], section=section, rating=4)
        rating2 = Rating(student=objects["student"], section=section2, rating=3)
        rating3 = Rating(student=objects["student2"], section=section, rating=2)
        self.session.add(objects["school"])
        self.session.add(objects["user"])
        self.session.add(objects["student"])
        self.session.add(objects["teacher"])
        self.session.add(course)
        self.session.add(section)
        self.session.add(rating)
        self.session.add(objects["user2"])
        self.session.add(objects["student2"])
        self.session.add(rating2)
        self.session.add(rating3)
        self.session.commit()
        self.assertEqual({rating2, rating, rating3}, set(objects["teacher"].ratings))

    def test_course_professors(self):
        objects = self.build_situation()
        self.session.add_all(objects.values())
        course = Course(name="mine", abbreviation="m", school=objects["school"])
        section = Section(professor=objects["teacher"], course=course, semester=1, year=2014)
        teacher2 = Faculty(school=objects["school"], account=objects["user"])
        section2 = Section(professor=teacher2, course=course, semester=2, year=2014)
        self.session.add_all([course, section, section2, teacher2])
        self.session.commit()
        self.assertEqual({teacher2, objects["teacher"]}, set(course.professors))

    def test_student_courses(self):
        objects = self.build_situation()
        self.session.add_all(objects.values())
        course = Course(name="mine", abbreviation="m", school=objects["school"])
        section = Section(professor=objects["teacher"], course=course, semester=1, year=2014)
        rating = Rating(section=section, student=objects["student"], rating=2)
        self.session.add_all([course, section, rating])
        self.session.commit()
        self.assertEqual([course], objects["student"].courses)

    def test_school_sections(self):
        objects = self.build_situation()
        self.session.add_all(objects.values())
        course = Course(name="mine", abbreviation="m", school=objects["school"])
        section = Section(professor=objects["teacher"], course=course, semester=1, year=2014)
        self.session.add_all([course, section])
        self.assertEqual([section], objects["school"].sections)


def tests():
    return unittest.TestLoader().loadTestsFromTestCase(TableTest)

if __name__ == "__main__":
    unittest.main()
