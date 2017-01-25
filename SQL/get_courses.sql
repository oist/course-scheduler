SELECT DISTINCT c.course_id, name, 
"length_of_class_in_minutes" length,
CONCAT( (SELECT last_name FROM faculty WHERE id=g.coordinator1) , coalesce((SELECT CONCAT(", ",last_name) FROM faculty WHERE id=g.coordinator2),'')),
"day_preference" day_pref,
"time_preference" time_pref

FROM course c JOIN gsclass g ON c.id = g.course_id
WHERE TYPE =  'elective'
AND class_id LIKE '2015_3_%' -- CHANGE YEAR AND TERM HERE
ORDER BY course_id

/* 
SELECT DISTINCT c.course_id, name, coalesce(lecture_hours + practical_hours,0), 
(SELECT last_name FROM faculty WHERE id=g.coordinator1) c1, 
coalesce((SELECT last_name FROM faculty WHERE id=g.coordinator2),'') c2

FROM course c JOIN gsclass g ON c.id = g.course_id
WHERE TYPE =  'elective'
AND class_id LIKE '2015_3_%' -- CHANGE YEAR AND TERM HERE
ORDER BY course_id
*/