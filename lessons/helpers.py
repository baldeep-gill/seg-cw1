from .models import User, StudentProfile

def find_next_available_student_number():
    """Will find the next available student number for a new student"""
    # id = 1
    # while Student.objects.filter(student_number=id):
    #     id += 1
    if(StudentProfile.objects.last()):
        return StudentProfile.objects.last().student_number + 1
    else:
        return 1