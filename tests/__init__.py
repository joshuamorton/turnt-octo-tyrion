import unittest
from tests import TableTest, DatabaseTest

__author__ = 'Josh'

modules = [
    TableTest.tests(),
    DatabaseTest.tests()
]

alltests = unittest.TestSuite(modules)


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(alltests)
