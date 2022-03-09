#!/usr/local/bin/python3
import pymysql
import collections
import os

def get_all_enrollments():
    db = pymysql.connect(host="dbc01.oist.jp",       # your host, usually localhost
                         user="gs_readonly",         # your username
                         passwd="REMOVED",  # your password
                         db="grad_school")           # name of the database

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    # Use all the SQL you like
    cur.execute("SELECT student_id, co.course_id \
                 FROM student_main s \
                 JOIN class_registration c ON s.id=c.student_main_id\
                 JOIN gsclass g ON g.id=c.gsclass_id\
                 JOIN course co ON co.id=g.course_id\
                 WHERE classification='OIST Student'\
                 ORDER BY preferred_n")

    enrollment = collections.defaultdict(set)

    for student, course in cur.fetchall():
        enrollment[course].add(student)

    db.close()
    return enrollment

def get_term_courses(year):

    db = pymysql.connect(host="dbc01.oist.jp",       # your host, usually localhost
                         user="gs_readonly",         # your username
                         passwd="REMOVED",  # your password
                         db="grad_school")           # name of the database

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    enrollments = []
    for term in [1,2,3]:
        cur.execute("SELECT co.course_id \
                     FROM gsclass g \
                     JOIN course co ON co.id=g.course_id\
                     WHERE class_id LIKE '{}_{}_%'\
                     AND co.course_id NOT IN (\"A406\",\"A407\",\"A408\", \
                                              \"IND\",\"IWS\",\"SPT\") \
                     ORDER BY course_id".format(year, term))

        enrollments.append(set(cur.fetchall()))

    db.close()
    return enrollments

def draw_chart(enrollment, courses, term):

    courses = sorted([c[0] for c in courses])

    chart_path = "GlobalCharts/courses_collisions_term_{}.tex".format(term)

    title = "Student Overlap Chart for all Years and Terms"

    width = 277/(len(courses)+1)
    height = 180/(len(courses)+1)

    # Writing LaTeX file
    f = open(chart_path, 'w')
    f.write("\\documentclass[landscape,a4paper]{article}\n"
            "\\usepackage[dvipsnames, table]{xcolor}\n"
            "\\usepackage{tikz, geometry}\n"
            "\\newgeometry{margin=1cm}\n"
            "\\begin{document}\n\n"
            "\\centering\n"
            "\\pagestyle{empty}\n\n")

    # Title
    f.write(title + "\n\\vspace{2mm}\n\n")
    f.write("\\begin{tikzpicture}\n")

    # General style
    f.write("\n% Cell style\n")
    f.write("\\tikzstyle{{cell}}=[draw, rectangle, minimum height={}mm, minimum width={}mm, anchor=north west]\n"
         .format(height, width))

    # Headers
    f.write("\n% Courses - Vertical\n")
    for i, course in enumerate(courses):
        f.write("\\node[cell] at (0, {}mm) {{{}}}; \n"
                .format(171-(i+1)*height, course))

    f.write("\n% Courses - Horizontal\n")
    for i, course in enumerate(courses):
        f.write("\\node[cell] at ({}mm,171mm) {{{}}}; \n"
                .format((i+1)*width, course))

    # Overlap
    f.write("\n% Overlap \n")
    for i, courseA in enumerate(courses):
        for j, courseB in enumerate(courses):
            overlap = len(enrollment[courseA].intersection(enrollment[courseB]))
            if i==j:
                f.write("\\node[cell, fill=Gray] at ({}mm,{}mm) {{{}}}; \n"
                        .format((i+1)*width, 171-(i+1)*height, overlap))
            elif overlap > 0:
                f.write("\\node[cell, fill = red] at ({}mm,{}mm) {{{}}}; \n"
                        .format((i+1)*width, 171-(j+1)*height, overlap))
            else:
                f.write("\\node[cell] at ({}mm,{}mm) {{}}; \n"
                        .format((i+1)*width, 171-(j+1)*height))


    f.write("\\end{tikzpicture}\n"
            "\\end{document}")
    f.close()

    os.system("pdflatex -output-directory=. {}".format(chart_path))
    os.system("rm *.aux *.log")

if __name__ == '__main__':
    all_enrollment = get_all_enrollments()
    term_courses = get_term_courses(2020)
    for term, courses in enumerate(term_courses):
        draw_chart(all_enrollment, courses, term + 1)
