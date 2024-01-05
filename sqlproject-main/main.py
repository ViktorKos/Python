from faker import Faker
import random
import psycopg2
from psycopg2 import sql

fake = Faker('uk_UA')

conn = psycopg2.connect(dbname='your_db_name', user='your_username', password='your_password', host='your_host', port='your_port')
cursor = conn.cursor()

for _ in range(3):
    cursor.execute("INSERT INTO groups (name) VALUES (%s);", (fake.word(),))

for _ in range(5):
    cursor.execute("INSERT INTO teachers (name) VALUES (%s);", (fake.name(),))

for _ in range(30):
    cursor.execute("INSERT INTO students (name, group_id) VALUES (%s, %s);", (fake.name(), random.randint(1, 3)))

for _ in range(8):
    cursor.execute("INSERT INTO subjects (name, teacher_id) VALUES (%s, %s);", (fake.word(), random.randint(1, 5)))

for student_id in range(1, 31):
    for subject_id in range(1, 9):
        for _ in range(20):
            cursor.execute("INSERT INTO grades (student_id, subject_id, grade, date) VALUES (%s, %s, %s, %s);",
                           (student_id, subject_id, random.uniform(60, 100), fake.date_this_decade()))

conn.commit()
conn.close()
