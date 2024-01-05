from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    grades = relationship('Grade', back_populates='student')

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    students = relationship('Student', back_populates='group')
    subjects = relationship('Subject', back_populates='group')

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    subjects = relationship('Subject', back_populates='teacher')

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    grades = relationship('Grade', back_populates='subject')

class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    value = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    student = relationship('Student', back_populates='grades')
    subject = relationship('Subject', back_populates='grades')

engine = create_engine('sqlite:///university.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
