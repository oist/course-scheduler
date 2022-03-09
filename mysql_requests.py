#!/usr/local/bin/python3
import pymysql
import os
import sys

def get_students(input_path, year, term):

    db = pymysql.connect(host="dbc01.oist.jp",       # your host, usually localhost
                         user="gs_readonly",         # your username
                         passwd="***REMOVED***",  # your password
                         db="grad_school")           # name of the database

    file_path = os.path.join(input_path, "{}_{}_students.csv".format(year, term))

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()
    f = open(file_path, "w")

    # Use all the SQL you like
    cur.execute("SELECT student_id, preferred_n, co.course_id \
                 FROM student_main s \
                 JOIN class_registration c ON s.id=c.student_main_id\
                 JOIN gsclass g ON g.id=c.gsclass_id\
                 JOIN course co ON co.id=g.course_id\
                 WHERE classification='OIST Student'\
                 AND class_id LIKE '{}_{}_%'\
                 ORDER BY preferred_n".format(year, term))

    f.write("Student ID,Student name,Class taken\n")
    for row in cur.fetchall():
        f.write(",".join(row) + "\n")

    db.close()
    f.close()

if __name__ == '__main__':
    try:
        year, term = map(int, sys.argv[1:])
        get_students("input_files", year, term)

    except ValueError:
        print("Two integer arguments needed. Ex: \n$ python3 mysql_requests.py 2018 1")
