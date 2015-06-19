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


def tests():
    return unittest.TestLoader().loadTestsFromTestCase(DatabaseTest)

if __name__ == "__main__":
    unittest.main()
