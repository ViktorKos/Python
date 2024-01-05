SELECT
    s.id,
    s.name AS student_name,
    g.grade,
    g.date
FROM
    students s
        JOIN
    grades g ON s.id = g.student_id
WHERE
        s.group_id = 1
  AND g.subject_id = 1;
