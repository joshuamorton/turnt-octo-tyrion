import unittest
import coverage
from tests import TableTest, DatabaseTest


__author__ = 'Josh'

modules = [
    TableTest.tests(),
    DatabaseTest.tests()
]

alltests = unittest.TestSuite(modules)


def test_coverage():
    cov = coverage.coverage()
    cov.start()
    unittest.TextTestRunner(verbosity=1).run(alltests)
    cov.stop()
    cov.html_report(directory='covhtml')

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(alltests)
