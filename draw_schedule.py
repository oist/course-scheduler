import random as rd
import os

def draw_schedule(year, term, csv_courses, csv_schedule, output_path):
    sch = open(csv_schedule,'r')
    try :
        sch = open(csv_schedule,'r')
    except IOError:
        print "Please enter a valid path for the CSV schedule"
        exit()

    try :
        crs = open(csv_courses,'r')
    except IOError:
        print "Please enter a valid path for the CSV courses"
        exit()

    schedule_path = csv_schedule.replace("csv", "tex")

    title = "Timetable for Year {}/{}, Term {}".format(year,year+1,term)

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    chunks = 30
    start_day = 9*60
    end_day = 17*60 + 30
    # total_width = 297 - 20  # A4 length in mm - 10mm margins

    # colors = ["Apricot", "Aquamarine", "Bittersweet", "Blue", "BlueGreen", "BrickRed",
    #           "BurntOrange", "CarnationPink", "Cyan", "Dandelion", "DarkOrchid",
    #           "Emerald", "Fuchsia", "Goldenrod", "Green", "GreenYellow", "JungleGreen", "Lavender",
    #           "LimeGreen", "Magenta", "Mahogany", "Maroon", "Melon", "MidnightBlue", "Mulberry", "NavyBlue",
    #           "Orange", "OrangeRed", "Orchid", "Peach", "Periwinkle", "PineGreen", "Plum", "Purple",
    #           "RawSienna", "Red", "RedOrange", "Rhodamine", "RoyalBlue", "RoyalPurple", "RubineRed", "Salmon",
    #           "SeaGreen", "SpringGreen", "Tan", "TealBlue", "Thistle", "Turquoise", "Violet",
    #           "VioletRed", "WildStrawberry", "Yellow", "YellowGreen", "YellowOrange"]

    colors = ["blue", "brown", "cyan", "Blue", "ForestGreen", "magenta", "olive", "orange", "Mahogany", "Sepia",
              "pink", "purple", "red", "teal", "violet", "black", "Gray", "Periwinkle",
              "Emerald", "Fuchsia", "Apricot"]

    # Importing name of courses and teachers
    courses = {}
    crs.readline()  # Skipping the first row
    for l in crs:
        id, name, length, teacher, days, starts = l.strip().split(',')  # course ID, name, length, teacher(s)
        # key = course ID, values = [course name, length, times per week, teacher]
        if courses.get(id) is None:
            col = rd.choice(colors)
            colors.remove(col)
            courses[id] = [name, teacher, col]
    crs.close()

    # Importing schedule
    schedule=[]
    sch.readline() # Skip the first line
    for l in sch:
        # Day,Start time,End time,Course ID,Room
        day, start, stop, course, room = l.strip().split(',')
        day=weekdays.index(day)
        x, y = map(int,start.split(':'))
        start = (x*60 + y - start_day)/chunks
        x, y = map(int,stop.split(':'))
        stop = (x*60 + y - start_day)/chunks - 1
        schedule.append([day, start, stop, room, course])
    sch.close()

    # Get number of columns
    timeslots = [[0 for j in range(len(weekdays))] for i in range(((end_day-start_day)/chunks+1))]
    width = [0 for j in range(len(weekdays))]
    for day, start, stop, room, course in schedule:
        for t in range(start, stop + 1):
            timeslots[t][day] += 1
            if width[day] < timeslots[t][day]:
                width[day] = timeslots[t][day]
    cellWidth = 200/sum(width)

    # Write individual cells
    cells = [["" for j in range(sum(width))] for i in range((end_day-start_day)/chunks+1)]
    for day, start, stop, room, course in schedule:
        d = sum(width[:day])
        while cells[start][d] != "":
            d += 1
        cells[stop][d] = "\\cellcolor{{{}!100}} \\multirow{{-{}}}{{{}mm}}{{" \
                "\\centering {{\\bfseries \\color{{white}} \\sffamily "\
                "{} ({})\\\\ {} \\\\ {} \\\\ {}:{:02d}--{}:{:02d}}}}}".format(
                        courses[course][2] , stop-start+1, cellWidth,
                        courses[course][0],  course,courses[course][1], room,
                        (start_day+start*chunks)/60, (start_day+start*chunks)%60,
                        (start_day+(stop+1)*chunks)/60,(start_day+(stop+1)*chunks)%60)
        for t in range(start, stop):
            cells[t][d] = "\\cellcolor{{{}!100}} ".format(courses[course][2])

    cells[6] = ["\\multicolumn{{{}}}{{c||}}{{\\multirow{{2}}*{{\\normalsize Lunch}}}}"
                    .format(width[k]) for k in range(len(weekdays)-1)]  # Lunch top
    cells[6].append("\\multicolumn{{{}}}{{c|}}{{\\multirow{{2}}*{{\\normalsize Lunch}}}}".format(width[-1]))
    cells[7] = ["\\multicolumn{{{}}}{{c||}}{{}}".format(width[k]) for k in range(len(weekdays)-1)]  # Lunch bottom
    cells[7].append("\\multicolumn{{{}}}{{c|}}{{}}".format(width[-1]))

    cells[14][sum(width[:3])] = "\\multicolumn{{{}}}{{c||}}{{\\multirow{{2}}*{{\\normalsize Tea Time}}}}".format(width[3])  # Tea time top
    cells[15][sum(width[:3])] = "\\multicolumn{{{}}}{{c||}}{{}}".format(width[3])   # Tea time bottom
    for k in range(width[3]-1): # Removes empty elements for tea time
        del cells[14][sum(width[:3])+1]
        del cells[15][sum(width[:3])+1]

    # Writing LaTeX file
    f = open(schedule_path, 'w')
    f.write("\\documentclass[landscape,a4paper]{article}\n"
            "\\usepackage{multirow, array, hhline}\n"
            "\\usepackage[dvipsnames, table]{xcolor}\n"
            "\\usepackage{type1cm, geometry}\n"
            "\\usepackage{color}\n"
            "\\newgeometry{margin=0.8cm}\n"
            "\\setlength{\\arrayrulewidth}{0.2pt}\n\n"
            "\\begin{document}\n"
            "\\pagestyle{empty}\n\n"
            "\\begin{table} \\centering\n"
            "\\fontsize{0.2cm}{0.3cm}\selectfont\n"
            "\\def\\arraystretch{3}\\noindent\n")
    f.write("{{\\normalsize {}}}\n".format(title))

    # Column sizes
    f.write("\\begin{tabular}{|p{8mm}|")
    for day in range(len(weekdays)):
        f.write("|" + "p{{{}mm}}|".format(cellWidth)*width[day])

    # top hhline
    f.write("}\n\\hhline{~")
    for day in range(len(weekdays)):
        f.write("|*{{{}}}{{-|}}".format(width[day]))
    f.write("}\n")

    # Weekdays
    f.write("\\multicolumn{1}{c|}{}")
    for day in range(len(weekdays)-1):
        f.write(" & \\multicolumn{{{}}}{{c||}}{{\\normalsize {}}}".format(width[day], weekdays[day]))
    f.write(" & \\multicolumn{{{}}}{{c|}}{{\\normalsize {}}}".format(width[-1], weekdays[-1]))

    # hhline below weekdays
    f.write(" \\\\ \\hhline{-:")
    for day in range(len(weekdays)):
        f.write(":*{{{}}}{{=:}}".format(width[day]))
    f.write("}\n")

    # main table
    f.write("\\multicolumn{1}{|c||}")
    for i, c in enumerate(cells):
        if i%2 == 0:
            f.write("{{\\normalsize {}:{:02d} }}& ".format((start_day+i*chunks)/60,(start_day+i*chunks)%60))
        else:
            f.write(" & ")
        f.write("&".join(c))
        if i == 5 or i == 7:
            f.write(" \\\\ \\hhline{-|")  # Lunch time hhline
            for day in range(len(weekdays)):
                f.write("|*{{{}}}{{-|}}".format(width[day]))
            f.write("}\n")
        elif i == 13 or i == 15:  # tea time hhline
            f.write(" \\\\ \\hhline{{-||*{{{}}}{{~}}||*{{{}}}{{-}}||}}\n".format(sum(width[:3]),width[3]))
        else:
            f.write(" \\\\ {}  \n".format("\\hhline{-||}"*(i%2==1 and i<len(cells)-1 )))  # Normal hhline

    f.write(" \\hhline{{-||{}}}\n \\end{{tabular}}\n"
            "\\end{{table}}\n\n"
            "\\end{{document}}".format("-"*sum(width)))
    f.close()

    os.system("pdflatex -output-directory={} {}".format(output_path, schedule_path))
    os.system("rm {0}/*.aux {0}/*.log".format(output_path))
