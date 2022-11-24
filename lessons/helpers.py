from .models import Student

def find_next_available_student_number():
    """Will find the next available student number for a new student"""
    if(Student.students.last()):
        return Student.students.last().id + 1 
    return 1