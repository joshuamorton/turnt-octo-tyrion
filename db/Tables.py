from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

__author__ = 'Josh'
Base = declarative_base()


class Account(Base):
    __tablename__ = "account"

    # basic (required) signup information
    uid = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    email_address = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    password_salt = Column(String(16), nullable=False)

    # An account could be both a student and a teacher, as in the case of a grad student
    # that TAs or teaches an undergraduate class
    student =  relationship("Student", backref="account", uselist=False)  # joins to student
    faculty =  relationship("Faculty", backref="account", uselist=False)  # joins to faculty


class Student(Base):
    __tablename__ = "student"
    uid = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("school.uid"))  # joins to school
    user_id = Column(Integer, ForeignKey("account.uid"))  # joins to account


class Faculty(Base):
    __tablename__ = "faculty"
    uid = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("school.uid"))  # joins to school
    user_id = Column(Integer, ForeignKey("account.uid"))  # joins to account


class School(Base):
    __tablename__ = "school"
    uid = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    abbreviation = Column(String(16), nullable=False, unique=True)
    students = relationship("Student", backref="school")  # 1-m joins to faculty
    faculty = relationship("Faculty", backref="school")  # 1-m joins to student

class Course(Base):
    __tablename__ = "course"
    uid = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(2000), nullable=True)
    abbreviation = Column(String(8), nullable=False)
    sections = relationship("Section", backref="course")

class Section(Base):
    __tablename__ = "section"
    uid = Column(Integer, primary_key=True)
    # semester
    # year
    # professor
    # etc.


