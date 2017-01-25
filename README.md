# course-scheduler
Python code to generate course schedules for the Graduate School

Method to generate the schedule

1. Pull the data from the mysql Grad School Database using the two scripts in the SQL folder (change the year and term accordingly)

2. Organize the data in csv files.
  - year_term_students.csv is the list of students ordered as: Student ID, Name, class taken. Multiple lines for multiple courses taken.
  - year_term_courses.csv is the list of courses ordered as: Course ID, Name, Length, Allowed Days, Allowed hours. Multiple lines for multiple occurences of classes. Allowed days is in the index of the day (0=Monday, 4=Friday), separated by ";" for multiple possibilities, no entry means no constraint. Allowed times is the possible starting times in minutes (9AM = 9*60 = 540), separated by ";" for multiple possibilities, no entry means no constraint.

3. Change the year and term in scheduler.py. Generate the schedule by running "python scheduler.py" in the terminal. The genetic algorithms generates a schedule using a random start so running the program twice will produce different results. The generation number and other parameters can be tweaked. The output will be a csv with the schedule, a warning text file with all the conflicts, a .tex file with a visualization of the schedule and a pdf with the schedule. Check if some text is missing in the shortest classes.

4. If changes are done by hand in the output csv (highly preferable to running a new solution every time), use "python scheduler.py modifiedschedule.csv" to check for possible conflicts. 
