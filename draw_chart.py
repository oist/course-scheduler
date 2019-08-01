#!/usr/local/bin/python3
import os

def draw_chart(year, term, student_in_courses, output_path):

    chart_path = os.path.join(output_path, "{}_{}_courses_collisions.tex"
                                            .format(year, term))

    sic = student_in_courses
    courses = sorted(sic.keys())
    title = "Student Overlap Chart for Year {}/{}, Term {}".format(year,year+1,term)

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
    f.write(title + "\n\\vspace{3mm}\n\n")
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
            overlap = len(set(sic[courseA]).intersection(sic[courseB]))
            if i==j:
                f.write("\\node[cell, fill=Gray] at ({}mm,{}mm) {{{}}}; \n"
                        .format((i+1)*width, 171-(i+1)*height, overlap))
            elif overlap > 0:
                f.write("\\node[cell, fill=Red] at ({}mm,{}mm) {{{}}}; \n"
                        .format((i+1)*width, 171-(j+1)*height, overlap))
            else:
                f.write("\\node[cell, fill=Green] at ({}mm,{}mm) {{{}}}; \n"
                        .format((i+1)*width, 171-(j+1)*height, overlap))


    f.write("\\end{tikzpicture}\n"
            "\\end{document}")
    f.close()

    os.system("pdflatex -output-directory={} {}".format(output_path, chart_path))
    os.system("rm {0}/*.aux {0}/*.log".format(output_path))
