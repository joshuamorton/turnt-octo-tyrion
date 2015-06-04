import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from db.Tables import School, Account, Student, Faculty, Base
from sqlalchemy import create_engine, MetaData


__author__ = 'Josh'

class TableTest(unittest.TestCase):

    def setUp(self):
        # creates an in memory db for testing
        engine = create_engine('sqlite://')  # in memory db
        self.metadata = Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

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
        self.assertEqual("bob",self.session.query(Account).all()[0].username)

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
        # a user account can be bound to boht a student and faculty instance, this checks
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



if __name__ == "__main__":
    unittest.main()