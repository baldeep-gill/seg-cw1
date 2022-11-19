from .models import Student

def find_next_available_student_number():
    """Will find the next available student number for a new student"""
    return Student.objects.last().id + 1 
