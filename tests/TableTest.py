import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from db.Tables import School, Account, Student, Faculty, Base
from sqlalchemy import create_engine, MetaData


__author__ = 'Josh'

class TableTest(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite://')  # in memory db
        self.metadata = Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

    def test_account_nulls(self):
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
        self.session.add(Account(username="bob", email_address="me@test.com",
                                 password_hash="secret", password_salt="table"))
        self.session.commit()
        self.assertEqual("bob",self.session.query(Account).all()[0].username)






if __name__ == "__main__":
    unittest.main()