from django import forms
from django.core.validators import RegexValidator
from .models import User, Student, StudentProfile, LessonRequest, Lesson
from django.db.models import Max
from .helpers import find_next_available_student_number
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateTimeField
from django.core.exceptions import ValidationError


from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def day_of_the_week_validator(value):
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    if value not in days:
        raise ValidationError(
            _('Needs to be a day of the week')
        )


"""Form for requesting a lesson"""
class LessonRequestForm(forms.ModelForm):
    class Meta:
        model = LessonRequest
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']
        """widgets = {
            'availability': forms.DateTimeInput()
        }"""

"""Form for booking a lesson request"""
class BookLessonRequestForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['duration','topic','teacher']

    start_date = forms.DateTimeField(label="Start Date",widget=forms.SelectDateWidget)
    day = forms.CharField(label="Day of the week",validators=[day_of_the_week_validator])
    time = forms.TimeField(label="Time")
    interval_between_lessons = forms.IntegerField(label="Weeks Between lessons")
    number_of_lessons = forms.IntegerField(label="NUmber of lessons")


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
        widgets = { 'bio': forms.Textarea() }

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

    def find_id_for_new_student(self):
        return Student.students.last().id + 1

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

