from sqlalchemy import func
from sqlalchemy.orm import aliased
from models import Session, Student, Subject, Grade, Teacher, Group

def select_1():
    session = Session()
    query = (
        session.query(Student, func.avg(Grade.value).label('avg_grade'))
        .join(Grade)
        .group_by(Student)
        .order_by(func.avg(Grade.value).desc())
        .limit(5)
    )
    result = query.all()
    session.close()
    return result

def select_2(subject_name):
    session = Session()
    query = (
        session.query(Student, func.avg(Grade.value).label('avg_grade'))
        .join(Grade)
        .join(Subject)
        .filter(Subject.name == subject_name)
        .group_by(Student)
        .order_by(func.avg(Grade.value).desc())
        .limit(1)
    )
    result = query.first()
    session.close()
    return result

def select_3(subject_name):
    session = Session()
    query = (
        session.query(Group, func.avg(Grade.value).label('avg_grade'))
        .join(Subject)
        .join(Grade)
        .filter(Subject.name == subject_name)
        .group_by(Group)
    )
    result = query.all()
    session.close()
    return result

def select_4():
    session = Session()
    query = session.query(func.avg(Grade.value).label('avg_grade'))
    result = query.scalar()
    session.close()
    return result

def select_5(teacher_name):
    session = Session()
    query = (
        session.query(Subject)
        .join(Teacher)
        .filter(Teacher.name == teacher_name)
    )
    result = [subject.name for subject in query.all()]
    session.close()
    return result

def select_6(group_name):
    session = Session()
    query = (
        session.query(Student)
        .join(Group)
        .filter(Group.name == group_name)
    )
    result = [student.name for student in query.all()]
    session.close()
    return result

def select_7(group_name, subject_name):
    session = Session()
    query = (
        session.query(Student, Grade.value)
        .join(Group)
        .join(Grade)
        .join(Subject)
        .filter(Group.name == group_name, Subject.name == subject_name)
    )
    result = [(student.name, grade) for student, grade in query.all()]
    session.close()
    return result

def select_8(teacher_name):
    session = Session()
    query = (
        session.query(Teacher, func.avg(Grade.value).label('avg_grade'))
        .join(Subject)
        .join(Grade)
        .filter(Teacher.name == teacher_name)
        .group_by(Teacher)
    )
    result = query.first()
    session.close()
    return result

def select_9(student_name):
    session = Session()
    query = (
        session.query(Subject)
        .join(Grade)
        .join(Student)
        .filter(Student.name == student_name)
    )
    result = [subject.name for subject in query.all()]
    session.close()
    return result

def select_10(student_name, teacher_name):
    session = Session()
    student_alias = aliased(Student)
    teacher_alias = aliased(Teacher)
    query = (
        session.query(Subject)
        .join(Grade)
        .join(student_alias)
        .join(teacher_alias)
        .filter(student_alias.name == student_name, teacher_alias.name == teacher_name)
    )
    result = [subject.name for subject in query.all()]
    session.close()
    return result

if __name__ == '__main__':
    # Виклик функцій вибірки
    print(select_1())
    print(select_2("Subject-1"))
    print(select_3("Subject-1"))
    print(select_4())
    print(select_5("Teacher-1"))
    print(select_6("Group-1"))
    print(select_7("Group-1", "Subject-1"))
    print(select_8("Teacher-1"))
    print(select_9("Student-1"))
    print(select_10("Student-1", "Teacher-1"))