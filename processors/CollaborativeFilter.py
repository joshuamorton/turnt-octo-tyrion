from sqlalchemy import func
from db.Tables import Student, Course

__author__ = 'Josh'
import math


class CollaborativeFilter:
    """
    A collaborative filter to be connected to a sqlalchemy database, one per ratable
     attribute
    """

    def __init__(self, database, attribute):
        """
        :param database: the database object
        :param attribute: one of the fields in the Rating table
        :return: None
        """
        self.database = database
        self.db = database
        self.attr = attribute
        self.db_cache = dict()
        self.similarity_cache = dict()
        self.calculated_cache = dict()

    def opinion(self, student, courseid, cache=True) -> float:
        db = self.db
        if cache:
            pass
        else:
            # calculates ratings without any use of a cache layer
            with db.scope as session:
                course = session.query(db.course).filter(db.course.uid == courseid).one()
                # get the single user
                user = session.query(db.student).filter(db.student.uid == student).one()
                # get all other users
                users = set(session.query(db.student).all()) - {user}
                k, total_rating = 0, 0
                for other in users:
                    simil = self.course_similarity(user.account.student, other.account.student, exclude=course)
                    total_rating += simil * self.db.query_rating(other, course, self.attr)
                    k += abs(simil)
            return total_rating / k


    def _rating_root_sum_squared(self, user: Student, exclude: Course=None) -> float:
        """
        Finds the root sum squared of all ratings by a given user.
        (\sqrt{\sum_{i\in I_x}{rating^2_{x,i}}})

        The tricky bit is that it aggregates by course not section.  This is generally not a problem, but in the case of
        a student taking a course repeatedly (research, failing, etc.) its necessary to merge all sections for the
        course into an overall number.  This is done with the rather complex join and groupby
        :param userid: the uid of the user
        :return: a float
        """
        attr = type(self.db.rating).__getattribute__(self.db.rating, self.attr)
        # kludgy workaround because rating is a class not an instance, so __getattribute__
        # expects to take an additional argument, and so
        # attr = self.db.rating.__getattribute__(self.attr) throws a typeerror
        if exclude is not None:
            excluded_id = exclude.uid
        else:
            excluded_id = None
        query = (self.db.session.query(func.avg(attr))
                 .join(self.db.student)
                 .join(self.db.section)
                 .join(self.db.course)
                 .filter(self.db.student.uid == user.uid)
                 .filter(self.db.course.uid != excluded_id)
                 .group_by(self.db.section.course_id).all())
        return math.sqrt(sum(x[0]**2 for x in query))

    def course_similarity(self, user: Student, other: Student, exclude:Course=None) -> float:
        """

        :param user:
        :param other:
        :param exclude:
        :return:
        """
        shared_courses = set(user.courses) & set(other.courses)
        ratings = [self.db.query_rating(user, course, self.attr)
                   * self.db.query_rating(other, course, self.attr) for course in shared_courses]

        return sum(ratings) / (self._rating_root_sum_squared(user, exclude=exclude) *
                               self._rating_root_sum_squared(other, exclude=exclude))
