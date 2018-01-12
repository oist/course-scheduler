SELECT student_id, preferred_n, co.course_id
FROM student_main s 
JOIN class_registration c ON s.id=c.student_main_id
JOIN gsclass g ON g.id=c.gsclass_id
JOIN course co ON co.id=g.course_id
WHERE classification='OIST Student'
AND class_id LIKE '2015_3_%'
ORDER BY preferred_n