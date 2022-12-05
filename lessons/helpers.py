from .models import Admin, Student, User, Invoice, Transfer, Term
from django.shortcuts import redirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


def find_next_available_student_number():
    """Will find the next available student number for a new student"""
    if(Student.students.last()):
        return Student.students.last().id + 1 
    return 1

def find_next_available_invoice_number_for_student(student):
    """Will find the next available invoice number for a given student"""
    invoices_for_student = Invoice.objects.filter(student=student)
    if(invoices_for_student.last()):
        return invoices_for_student.last().invoice_number + 1
    return 1

def find_next_available_transfer_id():
    """Will find the next available invoice number for a given student"""
    next_transfer_id = 1
    if Transfer.objects.last():
        next_transfer_id += Transfer.objects.last().transfer_id
    return next_transfer_id

'''decorator for preventing students and admins from accessing each other's pages'''
def only_students(view_function):
    def wrapper(request, *args, **kwargs):
        try:
            if Student.students.get(username=request.user.get_username()):
                return view_function(request, *args, **kwargs)
        except User.DoesNotExist:
            return redirect('admin_home')
    return wrapper


'''decorator for preventing students and admins from accessing each other's pages'''
def only_admins(view_function):
    def wrapper(request, *args, **kwargs):
        try:
            if Admin.admins.get(username=request.user.get_username()):
                return view_function(request, *args, **kwargs)

        except User.DoesNotExist:
            return redirect('student_home')
    return wrapper


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            try:
                if Admin.admins.get(username=request.user.get_username()):
                    return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_ADMIN)
            except User.DoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_STUDENT)
        else:
            return view_function(request)
    return modified_view_function

def day_of_the_week_validator(value):
    """Validates that the input to a field can only be a day of the week"""
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    if value not in days:
        raise ValidationError(
            _('Needs to be a day of the week')
        )

def is_a_term_validator(value):
    """Validates that the input is a term existing in the database"""
    all_terms = Term.objects.all()
    for term in all_terms:
        if value == term.name:
            return
    raise ValidationError(
        _('You need to input a valid school term!')
    )

def does_date_fall_in_an_existing_term(date_to_check):
    """Returns true if a date falls inside an existing term, false otherwise"""
    terms = Term.objects.all()
    for term in terms:
        if term.start_date <= date_to_check <= term.end_date:
            return True
    return False

def does_date_fall_in_given_term(date_to_check,term):
    """Returns true if a date falls inside given term, false otherwise"""
    if term.start_date <= date_to_check <= term.end_date:
        return True
    return False

def get_next_given_day_of_week_after_date_given(date,day):
    """Takes a date and a day of the week and returns the first date after passed in date on that day
    If the date passed in is on the passed in day of the week then just return"""
    weekday_dict = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
    while date.weekday() != weekday_dict[day]:
        tdelta = datetime.timedelta(days=1)
        date = date + tdelta
    return date

def get_next_term():
    """Gets the next upcoming term
    If already in a term, return the term we are currently in
    Return None if there are no terms"""
    if Term.objects.count() == 0:
        return None

    all_terms = Term.objects.all()
    next_term = None
    now = datetime.datetime.now()

    for term in all_terms:
        if term.start_date.timestamp() <= now.timestamp() <= term.end_date.timestamp():
            # We are currently in this term so return it
            return term

        time_until_term = term.start_date.timestamp() - now.timestamp()
        if time_until_term >= 0:
            if next_term == None or time_until_term < (next_term.start_date.timestamp() - now.timestamp()):
                next_term = term

    return next_term