from prettytable import PrettyTable
import os
from collections import defaultdict


class Student:
    _PT_FIELDS = ['CWID', 'Name', 'Major', 'Course']

    def __init__(self, cwid, name, major):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._courses = defaultdict(int)

    def add_course(self, course, grade):
        self._courses[course] = grade

    def pt_row(self):
        return [self._cwid, self._name, self._major, sorted(self._courses.keys())]


class Instructor:
    _PT_FIELDS = ['CWID', 'Name', 'Dept', 'Course', '# Student']

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
    except FileNotFoundError:
        raise FileNotFoundError("'can't open", path)
    else:
        with file_path as a:
            line_number = 0
            for line in a:
                line = line.strip()
                values = line.split(sep)
                line_number += 1
                if len(values) != fields:
                    raise ValueError(f'{path} has {len(values)} fields on line {line_number} but expected {len(values)}')
                elif header == True and line_number == 1:
                    continue
                else:
                    yield values


class Repository:

    def __init__(self, path, ptable=False):
        self._students = dict()
        self._instructors = dict()

        self._get_students(os.path.join(path, "students.txt"))
        self._get_instructors(os.path.join(path, "instructors.txt"))
        self._get_grades(os.path.join(path, "grades.txt"))

        if ptable:
            self.student_prettytable()
            self.instructor_prettytable()

    def _get_students(self, path):

        try:
            for cwid, name, major in file_reading_gen(path, 3, sep='\t', header=False):
                self._students[cwid] = Student(cwid, name, major)
        except FileExistsError as fee:
            print(fee)
        except ValueError as ve:
            print(ve)

    def _get_instructors(self, path):

        try:
            for cwid, name, dept in file_reading_gen(path, 3, sep='\t', header=False):
                self._instructors[cwid] = Instructor(cwid, name, dept)
        except FileExistsError as fee:
            print(fee)
        except ValueError as ve:
            print(ve)

    def _get_grades(self, path):
        try:
            for student_cwid, course, grade, instructor_cwid in file_reading_gen(path, 4, sep='\t', header=False):

                if student_cwid in self._students:
                    self._students[student_cwid].add_course(course, grade)
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
