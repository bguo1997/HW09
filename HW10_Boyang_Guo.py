import os
from prettytable import PrettyTable
from collections import defaultdict


class Major:
    _PT_FIELDS = ['DEPT', 'Required', 'Electives']

    def __init__(self, dept):
        self._dept = dept
        self._required = set()
        self._electives = set()

    def add_course(self, course, flag):
        if flag == 'R':
            self._required.add(course)
        elif flag == 'E':
            self._electives.add(course)
        else:
            raise ValueError(f"there isn't valid flag: {flag}")

    def pt_row(self):

        return self._dept, self._required, self._electives


class Student:
    _PT_FIELDS = ['CWID', 'NAME', 'Major', 'Completed Course', 'Remaining Required', 'Remaining Electives']

    def __init__(self, cwid, name, major, required_course, electives_course):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._courses = defaultdict(str)
        self._completed_courses = set()
        self._remaining_required = set.copy(required_course)
        self._remaining_electives = set.copy(electives_course)

    def add_course(self, course, grade):
        self._courses[course] = grade
        if grade in ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'):
            self._completed_courses.add(course)
            if course in self._remaining_electives:
                self._remaining_electives = None
            if course in self._remaining_required:
                self._remaining_required.remove(course)
        elif grade in ('D', 'D-', 'D+', 'E', 'E-', 'E+', 'F', 'F-', 'F+'):
            pass
        else:
            raise ValueError(f"there isn't valid grade: {grade}")

    def pt_row(self):
        return [self._cwid, self._name, self._major, sorted(self._completed_courses), sorted(self._remaining_required), sorted(self._remaining_electives) if self._remaining_electives != None else None]


class Instructor:
    _PT_FIELDS = ['CWID', 'Name', 'Dept', 'Course', 'Students']

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        self._courses = defaultdict(int)

    def add_course(self, course):
        self._courses[course] += 1

    def pt_row(self):
        for course, student in self._courses.items():
            yield [self._cwid, self._name, self._dept, course, student]


def file_reading_gen(path, fields, sep=',', header=False):
    try:
        file_path = open(path, 'r')
    except:
        raise FileNotFoundError("Can't open", path)
    else:
        with file_path as f:

            line_number = 0
            for line in f:
                line = line.strip("\n")
                values = line.split(sep)
                line_number += 1
                if len(values) != fields:
                    raise ValueError \
                        (f'{path} has {len(values)} fields on \
                            line {line_number} but expected {len(values)}')
                elif header == True and line_number == 1:
                    continue
                else:
                    yield values


class Repository:
    def __init__(self, path, ptable=False):
        self._major = dict()
        self._students = dict()
        self._instructors = dict()

        self._get_majors(os.path.join(path, "majors.txt"))
        self._get_students(os.path.join(path, "students.txt"))
        self._get_instructors(os.path.join(path, "instructors.txt"))
        self._get_grades(os.path.join(path, "grades.txt"))

        if ptable:
            self.major_prettytable()
            self.student_prettytable()
            self.instructor_prettytable()

    def _get_majors(self, path):
        try:
            for dept, flag, course in file_reading_gen(path, 3, sep='\t', header=True):
                if dept in self._major:
                    try:
                        self._major[dept].add_course(course, flag)
                    except ValueError as ve:
                        print(ve)
                else:
                    self._major[dept] = Major(dept)
                    try:
                        self._major[dept].add_course(course, flag)
                    except ValueError as ve:
                        print(ve)

        except FileExistsError as fnfe:
            print(fnfe)
        except ValueError as ve:
            print(ve)

    def _get_students(self, path):
        try:
            for cwid, name, major in file_reading_gen(path, 3, sep=';', header=True):
                try:
                    required_course = set.copy(self._major[major]._required)
                    electives_course = set.copy(self._major[major]._electives)
                except:
                    raise ValueError(f'No major named {major}')
                self._students[cwid] = Student(cwid, name, major, required_course, electives_course)
        except FileExistsError as fee:
            print(fee)
        except ValueError as ve:
            print(ve)

    def _get_instructors(self, path):
        try:
            for cwid, name, dept in file_reading_gen(path, 3, sep='|', header=True):
                self._instructors[cwid] = Instructor(cwid, name, dept)
        except FileExistsError as fee:
            print(fee)
        except ValueError as ve:
            print(ve)

    def _get_grades(self, path):
        try:
            for student_cwid, course, grade, instructor_cwid in file_reading_gen(path, 4, sep='|', header=True):
                if student_cwid in self._students:
                    try:
                        self._students[student_cwid].add_course(course, grade)
                    except ValueError as ve:
                        print(ve)
                else:
                    print(f"Found grade for unknown student {student_cwid}")
                if instructor_cwid in self._instructors:
                    self._instructors[instructor_cwid].add_course(course)
                else:
                    print(f"Found grade for unknown instructor {instructor_cwid}")

        except FileExistsError as fnfe:
            print(fnfe)
        except ValueError as ve:
            print(ve)

    def major_prettytable(self):
        pt = PrettyTable(field_names=Major._PT_FIELDS)
        for dept in self._major.values():
            pt.add_row(dept.pt_row())
        print(pt)

    def student_prettytable(self):
        pt = PrettyTable(field_names=Student._PT_FIELDS)
        for student in self._students.values():
            pt.add_row(student.pt_row())
        print(pt)

    def instructor_prettytable(self):
        pt = PrettyTable(field_names=Instructor._PT_FIELDS)
        for instructor in self._instructors.values():
            for row in instructor.pt_row():
                pt.add_row(row)
        print(pt)


def main():
    stevens = Repository("", True)


if __name__ == "__main__":
    main()
