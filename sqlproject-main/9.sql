SELECT
    s.name AS student_name,
    sub.name
FROM
    students s
        JOIN
    grades g ON s.id = g.student_id
        JOIN
    subjects sub ON g.subject_id = sub.id
WHERE
        s.id = 1;