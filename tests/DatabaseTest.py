import os
import unittest
from db import Database

__author__ = 'Josh'


class DatabaseTest(unittest.TestCase):
    def test_in_memory_creation(self):
        # just makes sure no error is thrown
        db = Database.Database(engine="sqlite://", name="", folder="")

    def create_in_memory(self):
        return Database.Database(engine="sqlite://", name="", folder="")

    def test_session(self):
        db = self.create_in_memory()
        with db.scope as sesh:
            school = db.school(name="Georgia Institute", abbreviation="gatech")
            sesh.add(school)

        with db.scope as sesh:
            sch = sesh.query(db.school).all()
            self.assertEqual(sch[0].name, "Georgia Institute")

    def test_overlapping_sessions(self):
        db = self.create_in_memory()

        with db.scope as sesh:
            school = db.school(name="Georgia Institute", abbreviation="gatech")
            sesh.add(school)

            with db.scope as sess:
                school2 = db.school(name="Massachusets Tech", abbreviation="MIT")
                sess.add(school2)
                self.assertEqual(1, len(sess.query(db.school).all()))

            schools = sesh.query(db.school).all()
            self.assertEqual(2, len(schools))


    def create_real_db(self):
        return Database.Database(name="test.db", folder=".")

    def test_db_persistence(self):
        db = self.create_real_db()
        with db.scope as sesh:
            school = db.school(name="Georgia Institute", abbreviation="gatech")
            sesh.add(school)

        del db
        db2 = self.create_real_db()
        with db2.scope as sesh:
            schools = sesh.query(db2.school).all()
            self.assertEqual("Georgia Institute", schools[0].name)

        os.remove('test.db')

def tests():
    return unittest.TestLoader().loadTestsFromTestCase(DatabaseTest)

if __name__ == "__main__":
    unittest.main()
