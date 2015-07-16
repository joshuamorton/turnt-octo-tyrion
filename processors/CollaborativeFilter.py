from sqlalchemy import func


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

    def opinion(self, student, section, cache=True):
        db = self.db
        if cache:
            pass
        else:
            # calculates ratings without any use of a cache layer
            with db.scope as session:
                # get the single user
                user = session.query(db.students).filter(db.students.uid == student).one()
                # get all other users
                users = {session.query(db.students).all()} - {user}
                courses = set(user.courses)
                shared = {other: courses & {other.courses} for other in users}

    def _rating_root_sum_squared(self, userid: int) -> float:
        """
        Finds the root sum squared of all ratings by a given user.
        (\sqrt{\sum_{i\in I_x}{rating^2_{x,i}}})

        The tricy bit is that it aggregates by course not section.  This is generally not a problem, but in the case of
        a student taking a course repeatedly (research, failing, etc.) its necessary to merge all sections for the
        course into an overall number.  This is done with the rather complex join and groupby
        :param userid: the uid of the user
        :return: a float
        """
        query = (self.db.session.query(func.avg(self.db.rating.rating))
                 .join(self.db.student)
                 .join(self.db.section)
                 .filter(self.db.student.uid == userid)
                 .group_by(self.db.section.course_id).all())
        return math.sqrt(sum(x[0]**2 for x in query))

    def course_similarity(self, username: str, othername: str) -> float:  # test this
        """
        get the coursewise similarity between two users (as opposed to section-wise)
        :param username: username for user
        :param othername: username for the other use
        :return: a float defining their similarity
        """
        with self.db.scope as session:
            user = self.db.student_with_name(username)
            other = self.db.student_with_name(othername)
            shared_courses = set(user.courses) & set(other.courses)
            ratings = [self.db.query_rating(user, course, self.attr)
                       * self.db.query_rating(other, course, self.attr) for course in shared_courses]

            return sum(ratings) / (self._rating_root_sum_squared(user.uid) * self._rating_root_sum_squared(other.uid))
