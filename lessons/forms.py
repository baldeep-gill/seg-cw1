from django import forms
from django.core.validators import RegexValidator, MinValueValidator
from .models import User, Student, StudentProfile, LessonRequest, Lesson, Guardian
from django.db.models import Max
from .helpers import find_next_available_student_number, day_of_the_week_validator
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateTimeField
from django.core.exceptions import ValidationError
import random

class LessonRequestForm(forms.ModelForm):
    """Form for requesting a lesson"""
    class Meta:
        model = LessonRequest
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']
        """widgets = {
            'availability': forms.DateTimeInput()
        }"""


class BookLessonRequestForm(forms.ModelForm):
    """Form for fulfilling/booking lesson requests"""
    class Meta:
        model = Lesson
        fields = ['duration','topic','teacher']

    start_date = forms.DateTimeField(label="Start Date",widget=forms.SelectDateWidget)
    day = forms.CharField(label="Day of the week",validators=[day_of_the_week_validator])
    time = forms.TimeField(label="Time")
    interval_between_lessons = forms.IntegerField(label="Weeks Between lessons",validators=[MinValueValidator(1)])
    number_of_lessons = forms.IntegerField(label="Number of lessons",validators=[MinValueValidator(1)])


class EditForm(forms.ModelForm):
    """Form to update lesson request"""
    class Meta:
        model = LessonRequest
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']

"""Forms for the lessons app."""
class LogInForm(forms.Form):
    username = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class StudentSignUpForm(forms.ModelForm):
    """Form enabling unregistered students to sign up."""

    class Meta:
        """Form options."""

        model = Student
        fields = ['first_name', 'last_name', 'email']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""
        new_student_number = find_next_available_student_number()

        super().save(commit=False)
        student = Student.objects.create_user(
            username = self.cleaned_data.get('first_name') + self.cleaned_data.get('last_name') + f'{new_student_number}' ,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )

        StudentProfile.objects.create(user=student, student_number = new_student_number)
        return student

class GuardianSignUpForm(forms.ModelForm):
    """Form enabling unregistered guardians to sign up."""

    class Meta:
        """Form options."""
        model = Guardian
        fields = ['first_name', 'last_name', 'email']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new guardian."""
        random_number = Guardian.objects.last().id + 1

        super().save(commit=False)
        guardian = Guardian.objects.create_user(
            username = self.cleaned_data.get('first_name') + self.cleaned_data.get('last_name') + f'{random_number}' ,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return guardian

class GuradianAddStudent(forms.Form):
    '''form enabling guardians to add students to their accounts'''
    student_first_name = forms.CharField(label='The Student\'s First Name')
    student_last_name = forms.CharField(label='The Student\' Last Name')
    student_email = forms.EmailField(label='The Student\' Email')

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        try:
            student = Student.students.get(email=self.cleaned_data.get('student_email'))
            if student.first_name != self.cleaned_data.get('student_first_name'):
                self.add_error('student_first_name', 'are you sure of the spelling?')

            if student.last_name != self.cleaned_data.get('student_last_name'):
                self.add_error('student_last_name', 'are you sure of the spelling?')

        except:
            self.add_error('student_email', 'this student does not exist >~<.')


class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']