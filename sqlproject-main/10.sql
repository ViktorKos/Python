SELECT
    s.name AS student_name,
    t.name AS teacher_name,
    sub.name
FROM
    students s
        JOIN
    grades g ON s.id = g.student_id
        JOIN
    subjects sub ON g.subject_id = sub.id
        JOIN
    teachers t ON sub.teacher_id = t.id
WHERE
        s.id = 2
  AND t.id = 1;