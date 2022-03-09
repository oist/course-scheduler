#!/usr/bin/env python3
import random as rd
import copy
import time
import os
import sys
import draw_schedule as ds
import mysql_requests as mysql
import draw_chart
import global_overlap

timestamp = int(time.time())
def hToMin(hour,minutes):
    return hour*60+minutes

def textToMin(time):
    h, m = map(int,time.split(':'))
    return hToMin(h,m)

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
chunks = 30  # Size of the time slots
start_day = hToMin(9,0)
end_day = hToMin(17,30)

# Importing schedule
def import_schedule(schedule_path):
    solution=[]
    with open(schedule_path,'r') as sch:
        sch.readline() # Skip the first line
        for l in sch:
            # Day, Start time, End time, Course ID, Room
            day, start, stop, course, room = l.strip().split(',')
            day=weekdays.index(day)
            x, y = map(int,start.split(':'))
            start = hToMin(x,y)
            x, y = map(int,stop.split(':'))
            stop = hToMin(x,y) - chunks
            solution.append([day, start, stop, room, course, -1])
    return solution

# Conflicts in the schedule
def checkschedule(solution, enrollment):
    with open(warning_path, 'w') as f:
        f.write("Warnings for {}\n".format(schedule_path))
        stu = {}  # student overlap
        co = {}  # Keeping track of courses
        overlap = [] # Course overlaps
        warn = []  # Warnings
        for (i, (day, start, stop, _, course, _)) in enumerate(solution):
            # Time related
            if hToMin(12,0) <= start < hToMin(13,0) or hToMin(12,0) < stop <= hToMin(13,0):
                warn.append("{}, {} happens during lunch".format(weekdays[day],course))

            if day == 3 \
              and (hToMin(16,0) <= start < hToMin(17,0) or hToMin(16,0) < stop <= hToMin(17,0)):
                warn.append("{}, {} happens during tea time".format(weekdays[day],course))


            for (day2, start2, stop2, _, course2, _) in solution[i+1:]:
                s12 = len(enrollment[course].intersection(enrollment[course2]))
                if course != course2 and day == day2 \
                  and course != "PD1" and course != "PD2" \
                  and (start <= start2 <= stop  or start <= stop2 <= stop) \
                  and s12 > 0 :
                    s1 = len(enrollment[course])
                    s2 = len(enrollment[course2])
                    percent = round(100 * s12 / min(s1,s2))
                    overlap.append((weekdays[day], course, s1, course2, s2, s12, percent))

        overlap.sort(key = lambda x : x[-1] , reverse = True)
        warn += [ "{}, {} ({}) and {} ({}) have had {} in common => {}%".format(*x) for x in overlap ]

        if warn == []:
            f.write("\nNo conflict detected\n")
        else:
            f.write("\n".join(warn))

if __name__ == '__main__':
   # mysql.get_students(input_path, year, term)
    try:
        year = int(sys.argv[1])
        term = int(sys.argv[2])
        schedule_path = sys.argv[3] # One argument: schedule mofified by hand

        input_path = "input_files"
        courses_path = os.path.join(input_path, "{}_{}_courses.csv".format(year, term))

        output_path = "output_files"
        warning_path = schedule_path.replace("schedule","warnings").replace("csv","txt")

        solution = import_schedule(schedule_path)
#        all_enrollment = global_overlap.get_all_enrollments()
        warning_path = schedule_path.replace("_schedule","_warnings").replace("csv","txt")
#        checkschedule(solution, all_enrollment)
        ds.draw_schedule(year, term, courses_path, schedule_path, output_path)

    except IndexError: # No arguments
        print("Add arguments: year, term, path to schedule")

