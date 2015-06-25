__author__ = 'Josh'

class CollaborativeFilter():
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

    def opinion(self, student, course):
        db = self.db



