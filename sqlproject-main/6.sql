SELECT
    s.id,
    s.name AS student_name
FROM
    students s
WHERE
        s.group_id = 1;
