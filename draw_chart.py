import os

def draw_chart(year, term, student_in_courses, output_path):

    chart_path = os.path.join(output_path, "{}_{}_courses_collisions.tex".format(year, term))

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

    # Courses
    f.write("\n% Courses - Vertical\n")
    for i, course in enumerate(courses):
        f.write("\\node[cell] at (0, {}mm) {{{}}}; \n".format(171-(i+1)*height, course))

    f.write("\n% Courses - Horizontal\n")
    for i, course in enumerate(courses):
        f.write("\\node[cell] at ({}mm,171mm) {{{}}}; \n".format((i+1)*width, course))

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




    # # Grid
    # f.write("\n% Grid\n")
    # f.write("\\tikzstyle{grid}=[draw, rectangle, minimum height=171mm, anchor=north west]\n")
    # pos = 12
    # for i, day in enumerate(weekdays):
    #     for j in range(width[i]):
    #             f.write("\\node[grid, minimum width={}mm] at ({}mm,-9mm) {{ }}; \n"
    #                     .format(cellWidth, pos))
    #             pos += cellWidth
    #     pos += 1
    #
    #
    # # Hours
    # f.write("\n% Hours\n")
    # f.write("\\tikzstyle{hours}=[draw, rectangle, minimum height=19mm, minimum width=11mm, anchor=north west]\n")
    # pos = -9
    # for i in range(9,18):
    #     f.write("\\node[hours, label={{[shift={{(0,-6mm)}}]north:{}:00}}] at (0,{}mm) {{}}; \n".format(i,pos))
    #     pos -= 19

    # # Schedule
    # f.write("\n% Schedule\n")
    # f.write("\\tikzstyle{{course}}=[draw, rectangle,anchor=north west,text centered,"
    #         "minimum width={}mm, text width={}mm]\n".format(cellWidth,0.82 *cellWidth))
    # xpos=11
    # for day in timeslots:
    #     xpos+=1
    #     for j in day:
    #         for day, start, stop, room, course in j:
    #             sizes={"x":xpos,
    #                    "y":-9-171.0*(start-start_day)/(end_day-start_day),
    #                    "height":171.0*(stop-start)/(end_day-start_day),
    #                    "color":courses[course][2],
    #                    "text":"{{\\bfseries \\color{{white}} \\sffamily \\tiny {}"\
    #                           " ({})"\
    #                           "\\\\ {} \\\\ {} \\\\ {}:{:02d}--{}:{:02d}}}"\
    #                           .format(courses[course][0], course,
    #                            courses[course][1], room, start/60, start%60,stop/60,stop%60)}
    #             f.write("\\node[course, minimum height={height}mm, fill={color}]" \
    #                     " at ({x}mm,{y}mm) \n {{{text}}}; \n".format(**sizes))
    #         xpos += cellWidth

    f.write("\\end{tikzpicture}\n"
            "\\end{document}")
    f.close()

    os.system("pdflatex -output-directory={} {}".format(output_path, chart_path))
    os.system("rm {0}/*.aux {0}/*.log".format(output_path))
