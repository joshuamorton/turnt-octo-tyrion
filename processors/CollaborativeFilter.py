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

                print(shared)

    def root_sum_squared(self, username):
        with self.db.scope as session:
            account = session.query(self.db.account).filter(self.db.account.username == username).one()
            return math.sqrt(sum(rating.__getattribute__(self.attr) ** 2 for rating in account.student.ratings))
