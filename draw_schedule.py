#!/usr/local/bin/python3
import random as rd
import os

def draw_schedule(year, term, csv_courses, csv_schedule, output_path):
    try :
        sch = open(csv_schedule,'r')
    except IOError:
        print("Please enter a valid path for the CSV schedule")
        exit()

    try :
        crs = open(csv_courses,'r')
    except IOError:
        print("Please enter a valid path for the CSV courses")
        exit()

    path_GS = csv_schedule.replace(".csv", "_GS.tex")
    path_stu = csv_schedule.replace(".csv", "_Students.tex")

    title = "Timetable for Year {}/{}, Term {}".format(year,year+1,term)

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    chunks = 30
    start_day = 9*60
    end_day = 18*60

    # colors = ["Apricot", "Aquamarine", "Bittersweet", "Blue", "BlueGreen", "BrickRed",
    #           "BurntOrange", "CarnationPink", "Cyan", "Dandelion", "DarkOrchid",
    #           "Emerald", "Fuchsia", "Goldenrod", "Green", "GreenYellow", "JungleGreen", "Lavender",
    #           "LimeGreen", "Magenta", "Mahogany", "Maroon", "Melon", "MidnightBlue", "Mulberry", "NavyBlue",
    #           "Orange", "OrangeRed", "Orchid", "Peach", "Periwinkle", "PineGreen", "Plum", "Purple",
    #           "RawSienna", "Red", "RedOrange", "Rhodamine", "RoyalBlue", "RoyalPurple", "RubineRed", "Salmon",
    #           "SeaGreen", "SpringGreen", "Tan", "TealBlue", "Thistle", "Turquoise", "Violet",
    #           "VioletRed", "WildStrawberry", "Yellow", "YellowGreen", "YellowOrange"]

    colors = ['Apricot', 'Blue', 'Emerald', 'ForestGreen', 'Fuchsia', 'Gray',
               'Mahogany', 'Periwinkle', 'Sepia', 'Thistle', 'black', 'blue',
               'brown', 'cyan', 'magenta', 'olive', 'orange', 'Peach', 'pink',
               'purple','red', 'teal', 'violet', 'YellowOrange', 'TealBlue', 'Melon']

    # Importing name of courses and teachers
    courses = {}
    crs.readline()  # Skipping the header
    for l in crs:
        id, name, length, teacher, days, starts = l.strip().split(',')  # course ID, name, length, teacher(s)
        # key = course ID, values = [course name, length, times per week, teacher]
        if courses.get(id) is None:
            if len(colors)==0:
                print("Not enough colors in the list, exiting")
                exit()
            col = rd.choice(colors)
            colors.remove(col)
            courses[id] = [name, teacher, col]
    crs.close()

    # Importing schedule
    schedule=[]
    sch.readline() # Skip the header
    for l in sch:
        # Day,Start time,End time,Course ID,Room
        day, start, stop, course, room = l.strip().split(',')
        day=weekdays.index(day)
        x, y = map(int,start.split(':'))
        start = x*60 + y
        x, y = map(int,stop.split(':'))
        stop = x*60 + y
        schedule.append([day, start, stop, room, course])
    sch.close()

    # Get timeslots
    timeslots = [[[]] for i in weekdays]
    width = [0 for i in weekdays]
    for day, start, stop, room, course in schedule:
        j=0
        while not all([start>=c[2] or stop <=c[1]  for c in timeslots[day][j] ]) :
            if j<len(timeslots[day]) -1:
                j+=1
            else:
                timeslots[day].append([])
        timeslots[day][j].append([day, start, stop, room, course])
        width[day] = max(width[day], j+1)
    cellWidth = 263/sum(width)

    def write_file(schedule_path, for_GS):
        # Writing LaTeX file
        f = open(schedule_path, 'w')
        f.write("\\documentclass[landscape,a4paper]{article}\n"
                "\\usepackage[dvipsnames, table]{xcolor}\n"
                "\\usepackage{tikz, geometry}\n"
                "\\newgeometry{margin=1cm}\n"
                "\\begin{document}\n\n"
                "\\centering\n"
                "\\pagestyle{empty}\n\n")

        # Title
        f.write(title + "\n\\vspace{3mm}\n\n")
        f.write("\\begin{tikzpicture}[x=277mm, y=-180mm]\n")

        # Weekdays and grid
        f.write("\n% Days\n")
        f.write("\\tikzstyle{day}=[draw, rectangle, minimum height=8mm, anchor=north west]\n")
        pos = 12
        for i, day in enumerate(weekdays):
            f.write("\\node[day, minimum width={}mm] at ({}mm,0) {{{}}}; \n"
                    .format(cellWidth*width[i], pos, day))
            pos += cellWidth*width[i] + 1

        # Grid
        f.write("\n% Grid\n")
        f.write("\\tikzstyle{grid}=[draw, rectangle, minimum height=171mm, anchor=north west]\n")
        pos = 12
        for i, day in enumerate(weekdays):
            for j in range(width[i]):
                    f.write("\\node[grid, minimum width={}mm] at ({}mm,-9mm) {{ }}; \n"
                            .format(cellWidth, pos))
                    pos += cellWidth
            pos += 1

        # Lunch
        f.write("\n% Lunch\n")
        f.write("\\tikzstyle{lunch}=[draw, rectangle, minimum height=19mm, anchor=north west, fill=white]\n")
        pos = 12
        for i, day in enumerate(weekdays):
            f.write("\\node[lunch, minimum width={}mm] at ({}mm,-66mm) {{Lunch}}; \n" \
                    .format(cellWidth*width[i], pos))
            pos += cellWidth*width[i] + 1

        # Tea time ### change align=center/right if there is/isn't class on Tea Time
        f.write("\n% Time\n")
        f.write("\\node[lunch, minimum width={}mm, text width={}mm, align=center] at ({}mm,-142mm) {{Tea Time}}; \n" \
            .format(cellWidth*width[3],cellWidth*width[3]/2, 15+cellWidth*sum(width[:3])))

        # Hours
        f.write("\n% Hours\n")
        f.write("\\tikzstyle{hours}=[draw, rectangle, minimum height=19mm, minimum width=11mm, anchor=north west]\n")
        pos = -9
        for i in range(9,18):
            f.write("\\node[hours, label={{[shift={{(0,-6mm)}}]north:{}:00}}] at (0,{}mm) {{}}; \n".format(i,pos))
            pos -= 19

        # Schedule
        f.write("\n% Schedule\n")
        f.write("\\tikzstyle{{course}}=[draw, rectangle,anchor=north west,text centered,"
                "minimum width={}mm, text width={}mm]\n".format(cellWidth,0.82 *cellWidth))

        xpos=11
        for day in timeslots:
            xpos+=1
            for j in day:
                for day, start, stop, room, course in j:
                    if for_GS:
                        course_code = " ({})".format(course)
                    else:
                        course_code = ""

                    sizes={"x":xpos,
                           "y":-9-171.0*(start-start_day)/(end_day-start_day),
                           "height":171.0*(stop-start)/(end_day-start_day),
                           "color":courses[course][2],
                           "text":"{{\\bfseries \\color{{white}} \\sffamily \\tiny {}{}"\
                                  "\\\\ {} \\\\ {} \\\\ {}:{:02d}--{}:{:02d}}}"\
                                  .format(courses[course][0], course_code,
                                   courses[course][1], room, start//60, start%60,stop//60,stop%60)}
                    f.write("\\node[course, minimum height={height}mm, fill={color}]" \
                            " at ({x}mm,{y}mm) \n {{{text}}}; \n".format(**sizes))
                xpos += cellWidth

        f.write("\\end{tikzpicture}\n"
                "\\end{document}")
        f.close()

    for path, for_GS in [(path_GS, True), (path_stu, False)]:
        write_file(path, for_GS)
        os.system("pdflatex -output-directory={} {}".format(output_path, path))
        os.system("rm {0}/*.aux {0}/*.log".format(output_path))
