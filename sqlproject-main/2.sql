SELECT
    s.id,
    s.name AS student_name,
    AVG(g.grade) AS average_grade
FROM
    students s
        JOIN
    grades g ON s.id = g.student_id
WHERE
        g.subject_id = 1
GROUP BY
    s.id, s.name
ORDER BY
    average_grade DESC
LIMIT 1;