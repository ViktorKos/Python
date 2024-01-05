from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from models import Base, Student, Group, Teacher, Subject, Grade
from random import randint, choice

fake = Faker()

engine = create_engine('sqlite:///university.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

groups = [Group(name=f"Group-{i}") for i in range(1, 4)]
session.add_all(groups)
session.commit()

teachers = [Teacher(name=fake.name()) for _ in range(5)]
session.add_all(teachers)
session.commit()

subjects = [Subject(name=f"Subject-{i}", teacher=choice(teachers), group=choice(groups)) for i in range(1, 9)]
session.add_all(subjects)
session.commit()

students = [Student(name=fake.name(), group=choice(groups)) for _ in range(50)]
session.add_all(students)
session.commit()

for student in students:
    for subject in subjects:
        grade_value = round(randint(70, 100) / 10, 1)
        grade = Grade(value=grade_value, student=student, subject=subject)
        session.add(grade)
session.commit()