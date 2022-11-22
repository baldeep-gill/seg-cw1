from .models import Admin, Student, User
from django.shortcuts import redirect


def find_next_available_student_number():
    """Will find the next available student number for a new student"""
    if(Student.students.last()):
        return Student.students.last().id + 1 
    return 1

'''decorator for preventing students and admins from accessing each other's pages'''
def only_students(view_function):
    def wrapper(request):
        try:
            if Student.students.get(username=request.user.get_username()).exists():
                return view_function(request)
        except User.DoesNotExist:
            return redirect('admin_home')
    return wrapper


'''decorator for preventing students and admins from accessing each other's pages'''
def only_admins(view_function):
    def wrapper(request):
        try:
            if Admin.admins.get(username=request.user.get_username()).exists():
                return view_function(request)
        except User.DoesNotExist:
            return redirect('student_home')
    return wrapper