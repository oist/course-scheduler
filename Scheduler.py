import random as rd
import copy
import time
import os
import sys
import draw_schedule as ds

'''
TO DO:
- teaching labs
- seed with last year's solution
- room preferences

'''

year = 2016
term = 2


timestamp = int(time.time())

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
chunks = 30  # Size of the time slots
start_day = 9*60
end_day = 17*60 + 30


# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

input_path = "input_files"
rooms_path = os.path.join(application_path, input_path, "rooms.csv")
courses_path = os.path.join(application_path, input_path, "{}_{}_courses.csv".format(year, term))
students_path = os.path.join(application_path, input_path, "{}_{}_students.csv".format(year, term))

output_path = "output_files"
sic_path = os.path.join(application_path, output_path, "{}_{}_student_in_courses.txt".format(year, term))
schedule_path = os.path.join(application_path, output_path, "{}_{}_{}_schedule.csv".format(year, term, timestamp))
warning_path = schedule_path.replace("schedule","warnings").replace("csv","txt")


class Schedule:
    def __init__(self, size=1000, mutation_rate=0.05, to_select=100, generations=400):
        # Initializing constants
        self.size = size
        self.mutation_rate = mutation_rate
        self.to_select = to_select
        self.gen = generations

        # Getting data from courses.csv, rooms.csv and students.csv
        self.rooms = self.import_rooms()
        self.timeslots = self.generate_timeslots()
        self.courses = self.import_courses()
        self.students = self.import_students()
        self.student_in_courses = self.get_student_in_courses()

        self.solution = []
        self.final_fitness = 0

    def build(self):
        # Initial random population
        population = self.initialize_pop(self.size)

        # Start the genetic evolution process
        selected_pop, top_fitness = [], 9999999999
        for k in range(self.gen):
            # Calculate the fitness of each creature
            fit = [self.fitness(p) for p in population]
            # Selecting the best creatures
            selected_pop, top_fitness = self.select_top(population, fit)
            self.solution = copy.deepcopy(selected_pop[0])
            self.final_fitness = top_fitness
            print k + 1, top_fitness
            # Stop if we find a perfect solution
            if top_fitness == 0: break
            # Breed the next generation
            population = self.breed_population(selected_pop)

        # Saving best solution
        self.export_schedule(self.solution)
        self.checkschedule()

    # Reading data from a csv file containing info about the rooms
    def import_rooms(self):
        # features (0 or 1): Projector, Window, Blackboard, Whiteboard, Monitor,
        #       Multiple boards, Simultaneous board and screen/monitor, Seminar type
        rooms = {}  # Available rooms
        f = open(rooms_path, 'r')
        f.readline()  # Skipping the first row
        for l in f:
            data = l.strip().split(',')  # name, features (see above)
            # key = room name, values = [features of the room]
            rooms[data[0]] = map(int, data[1:])
        f.close()
        return rooms

    # Reading data from a csv file containing info about the courses
    def import_courses(self):
        courses = {}

        # Key = course ID, values = [name, teacher, class number, possible days, possible starts]
        f = open(courses_path, 'r')
        # f.readline()  # Skipping the first row
        for l in f:
            # course ID, name, length, teacher, possible days, possible starts
            id, name, length, teacher, days, starts = l.strip().split(',')
            length = int(length)
            days = [int(d) for d in days.split(';') if d != '']
            starts = [int(s) for s in starts.split(';') if s != '']

            if courses.get(id) is None:
                courses[id] = [[name, teacher, length, days, starts]]
            else:
                courses[id].append([name, teacher, length, days, starts])
        f.close()
        return courses

    # Reading data from a csv file containing info about the students
    def import_students(self):
        students = {}
        f = open(students_path, 'r')
        # f.readline()  # Skipping the first row
        for l in f:
            id, name, course = l.strip().split(',')  # ID, name, course
            # key = ID, values = [name, course]
            if students.get(id) is None:
                students[id] = [name, course, "SC"]  # Adding Skill Clinic for every student
                if id[:2] == str(year % 100):
                    students[id].append("JP1")
                    students[id].append("PD1")
                else:
                    students[id].append("PD2")
            else:
                students[id].append(course)
        f.close()
        return students

    # Generates all the possible timeslot/room combinations in chunks of chunks minutes
    def generate_timeslots(self):
        ts = []
        for day in range(len(weekdays)):  # Every day in the week
            for time in range(start_day, end_day, chunks):  # Every chunks minute slice from 9 to 17:30
                if time != 12*60 or not(day==3 and time==16*60): # Avoid lunch and tea time completely
                    for room in self.rooms.keys():
                        ts.append([day, time, room])
        return ts

    # Lists each participants per course, prints a message when a course picked isn't in the list
    def get_student_in_courses(self):
        sic = {}
        nonav = []
        for id in self.students.keys():
            for course in self.students[id][1:]:
                if course not in self.courses.keys():
                    if course not in nonav:
                        print "\n{} not in the list of available courses".format(course)
                        nonav.append(course)
                else:
                    if sic.get(course) is None:
                        sic[course] = [id]
                    else:
                        sic[course].append(id)

        f = open(sic_path, 'w')
        for course in sic:
            name_id = ["{} ({})".format(self.students[id][0], id) for id in sic[course]]
            f.write("Students in course {}: {}\n".format(course, ", ".join(name_id)))
        f.close()

        return sic

    # Checks if a timeslot is available
    def free_slot(self, day, start, room, length, timeslots):
        # Return true if all the consecutive chunks minute slots for the course are available
        return all([([day, start + k * chunks, room] in timeslots) for k in range(length / chunks)])

    # Initializes a population of random schedules
    def initialize_pop(self, size):
        pop = []  # new population
        for i in range(size):
            p = self.random_creature()
            if p:
                pop.append(p)
        return pop

    # Makes a random creature
    def random_creature(self):
        p = []  # new creature
        ts = list(self.timeslots)
        for course in self.student_in_courses.keys():
            for session in range(len(self.courses[course])):
                length = self.courses[course][session][2]
                day, room, start = 0, 0, 0
                count = 0
                # Keep picking random slots until one is available
                while not self.free_slot(day, start, room, length, ts):
                    count += 1
                    if count > 100:
                        return 0

                    if self.courses[course][session][3]:
                        day = rd.choice(self.courses[course][session][3])
                    else:
                        day = rd.randint(0, len(weekdays) - 1)

                    if self.courses[course][session][4]:
                        start = rd.choice(self.courses[course][session][4])
                    else:
                        start = rd.choice(range(start_day, end_day, chunks))

                    room = rd.choice(self.rooms.keys())

                for k in range(length / chunks):
                    ts.remove([day, start + k * chunks, room])
                # Structure: day, start time, stop time, room, course, session. Course is fixed.
                p.append([day, start, start + length - chunks, room, course, session])
        return p

    # Fitness function for the schedule
    def fitness(self, schedule):
        fit = 0
        stu = {}  # student overlap
        ro = {}  # different rooms
        co = {}  # Keeping track of courses
        for (day, start, stop, room, course, session) in schedule:
            # Time related
            for time in range(start, stop + 1, chunks):
                if 12 * 60 <= time < 13 * 60: fit += 3000  # Lunch time
                if day == 3 and 16 * 60 <= time < 17 * 60: fit += 2000  # Tea time

                # Start checking for overlapping students
                exact_time = day * 10000 + time
                if stu.get(exact_time) is None:
                    stu[exact_time] = list(self.student_in_courses[course])
                    co[exact_time] = [course] * len(self.student_in_courses[course])
                else:
                    for student in self.student_in_courses[course]:
                        if student in stu[exact_time]:
                            if course == "JP1" or co[exact_time][stu[exact_time].index(student)] == "JP1":
                                fit += 1000  # Not too bad if it's Japanese class
                            else:
                                fit += 10000  # Overlapping student
                        else:
                            stu[exact_time].append(student)
                            co[exact_time].append(course)

            # Space related
            if ro.get(course) is None:
                ro[course] = room
            else:
                if ro[course] != room:
                    fit += 500  # Same class should use same rooms

        return fit

    # Selecting the top schedules
    def select_top(self, population, fitness):
        indx = sorted(range(len(population)), key=lambda k: fitness[k])
        return [copy.deepcopy(population[i]) for i in indx[:self.to_select]], fitness[indx[0]]

    # Making baby schedules
    def breed_population(self, top_pop):
        # p = []
        p = copy.deepcopy(top_pop)  # Elitism
        # for i in range(self.size/100):  # Adding some random genes
        #     p.append(self.random_creature())

        for k in range(self.size - len(p)):
            # Gene splicing
            p1 = list(rd.choice(top_pop))
            p2 = list(rd.choice(top_pop))
            cutoff1, cutoff2 = sorted([rd.randint(1, len(p1) - 1), rd.randint(1, len(p1) - 1)])
            baby = p1[:cutoff1] + p2[cutoff1:cutoff2] + p1[cutoff2:]

            # Start mutations
            for slot in baby:  # slot = [day, start time, stop time, room, course, session]
                # Mutating day
                if rd.random() < self.mutation_rate:
                    if self.courses[slot[4]][slot[5]][3]:
                        slot[0] = rd.choice(self.courses[slot[4]][slot[5]][3])
                    else:
                        slot[0] = (slot[0] + rd.choice([-1, 1])) % len(weekdays)

                # Mutating time
                if rd.random() < self.mutation_rate:
                    if self.courses[slot[4]][slot[5]][4]:
                        dt = rd.choice(self.courses[slot[4]][slot[5]][4]) - slot[1]
                    else:
                        dt = rd.choice([-2 * chunks, -chunks, chunks, 2 * chunks])

                    if slot[1] + dt >= start_day and slot[2] + dt < end_day:
                        slot[1] += dt
                        slot[2] += dt

                # Mutating room
                if rd.random() < self.mutation_rate:
                    slot[3] = rd.choice(self.rooms.keys())  # Random change in room

            p.append(baby)
        return p

    def print_schedule(self, schedule):
        # Sort the schedule items by weekday and time
        for p in sorted(schedule, key=lambda k: k[0] * 10000 + k[1]):
            s = "{}, from {}:{:02d} to {}:{:02}, course {} ({}, {}) in {} (" \
                .format(weekdays[p[0]], p[1] / 60, p[1] % 60, (p[2] + chunks) / 60, (p[2] + chunks) % 60
                        , p[4], self.courses[p[4]][0][0], self.courses[p[4]][0][1], p[3])
            s += ", ".join([self.students[id][0] for id in self.student_in_courses.get(p[4])])
            s += ")"
            print s

    def export_schedule(self, schedule):
        f = open(os.path.join(application_path, schedule_path), "w")
        f.write("Day,Start time,End time,Course ID,Room\n")
        for p in sorted(schedule, key=lambda k: k[0] * 10000 + k[1]):
            f.write("{},{}:{:02d},{}:{:02d},{},{}\n".format(weekdays[p[0]], p[1] / 60, p[1] % 60, (p[2] + chunks) / 60,
                                                            (p[2] + chunks) % 60, p[4], p[3]))
        f.close()

    # Importing schedule
    def import_schedule(self, schedule_path):
        self.solution=[]
        sch = open(schedule_path,'r')
        sch.readline() # Skip the first line
        for l in sch:
            # Day, Start time, End time, Course ID, Room
            day, start, stop, course, room = l.strip().split(',')
            day=weekdays.index(day)
            x, y = map(int,start.split(':'))
            start = x*60 + y
            x, y = map(int,stop.split(':'))
            stop = x*60 + y - chunks
            self.solution.append([day, start, stop, room, course, -1])
        sch.close()

    # Conflicts in the schedule
    def checkschedule(self):
        f = open(warning_path, 'w')
        f.write("Warnings for {}\n".format(schedule_path))
        stu = {}  # student overlap
        co = {}  # Keeping track of courses
        warn = ""  # Warnings
        for (day, start, stop, room, course, session) in self.solution:
            # Time related
            for time in range(start, stop + 1, chunks):
                s = "\n{}, from {}:{:02d} to {}:{:02}, course {} in {}" \
                    .format(weekdays[day], time / 60, time % 60, (time + chunks) / 60, (time + chunks) % 60, course,
                            room)
                if 12 * 60 <= time < 13 * 60:  # Lunch time
                    warn += s + " happens during lunch"
                if day == 3 and 16 * 60 <= time < 17 * 60:  # Tea time
                    warn += s + " happens during tea time"

                # Start checking for overlapping students
                exact_time = day * 10000 + time
                if stu.get(exact_time) is None:
                    stu[exact_time] = list(self.student_in_courses[course])
                    co[exact_time] = [course] * len(self.student_in_courses[course])
                else:
                    for student in self.student_in_courses[course]:
                        if student in stu[exact_time]:
                            warn += s + ", student {} is also supposed to be in course {}" \
                                .format(student, co[exact_time][stu[exact_time].index(student)])
                        else:
                            stu[exact_time].append(student)
                            co[exact_time].append(course)
        if warn == "":
            f.write("\nNo conflict detected\n")
        else:
            f.write(warn)
        f.close()


if __name__ == '__main__':
    s = Schedule()
    try:
        schedule_path = sys.argv[1]
        s.import_schedule(schedule_path)
        warning_path = schedule_path.replace("schedule","warnings").replace("csv","txt")
        s.checkschedule()

    except IndexError:
        s.build()
        print "\nThe final fitness is {}".format(s.final_fitness)

    ds.draw_schedule(year, term, courses_path, schedule_path, output_path)
