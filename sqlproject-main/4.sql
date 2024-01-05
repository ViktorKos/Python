SELECT
    t.name AS teacher_name,
    s.subject_name
FROM
    teachers t
JOIN
    subjects s ON t.teacher_id = s.teacher_id
WHERE
    t.teacher_id = 1;