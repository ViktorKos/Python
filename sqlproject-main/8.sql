SELECT
    t.name AS teacher_name,
    AVG(g.grade) AS average_grade
FROM
    teachers t
        JOIN
    subjects s ON t.id = s.teacher_id
        JOIN
    grades g ON s.id = g.subject_id
GROUP BY
    t.name, t.id;
