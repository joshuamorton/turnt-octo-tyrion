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
                # Dict[User, Set[Course]] where each Set[Course] is the set of courses
                # taken by 'user' and the dict key

                # the similarity is defined as
                # r_{u, i} = k \sum_{u' \in U}{simil(u, u') * r_{u', i}}
                # where k = 1 / \sum_{u' \in U}{|simil(u, u') * r_{u', i}|}
                # and simil(a, b) is the cosine distance of a and b

    def rating_root_sum_squared(self, userid):
        with self.db.scope as session:
            return math.sqrt(sum(rating.__getattribute__(self.attr) ** 2 for rating in self.db.student_with_id(userid).ratings))

    def course_similarity(self, username, othername):  # test this
        with self.db.scope as session:
            user = self.db.student_with_name(username)
            other = self.db.student_with_name(othername)
            shared_courses = set(user.courses) & set(other.courses)
            ratings = [self.db.query_rating(user, course, self.attr) * self.db.query_rating(other, course, self.attr) for course in shared_courses]

            return sum(ratings) / (self.rating_root_sum_squared(user.uid) * self.rating_root_sum_squared(other.uid))

